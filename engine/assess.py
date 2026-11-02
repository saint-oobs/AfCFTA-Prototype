"""Pipeline stage 4 (Output): deterministic rule check for HS heading 19.01.

Order: retrieval -> input classification -> evidence gate -> tolerance (exact) ->
Article 7(1) -> Article 7(2) -> packaging / other evidence -> outcome -> folder.
All comparisons are plain code on Decimal values. No language model is called here.
"""
import re
from decimal import Decimal, getcontext

from .util import heading_of, chapter_of, money, fmt, USABLE
from .folder import build_folder

ENGINE_VERSION = "1.2.0"  # 1.2.0: plain-language requirement table (no rule change)
# 1.1.0  # 1.1.0: Art. 7(2) food-aid check also runs when the product is out of the rule base (revision R2)
getcontext().prec = 34  # only used for display values; comparisons are cross-multiplied

LIKELY = "Likely to qualify"
UNLIKELY = "Likely not to qualify"
FIR = "Further information required"
SEV_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}
CAT_ORDER = {"rule_1901": 0, "article7": 1, "food_aid": 2, "hs": 3, "origin_proof": 4,
             "value": 5, "consistency": 6, "process": 7, "packaging": 8, "form": 9}
DISCLAIMER = ("Synthetic data – prototype – indicative only. The official decision is made by "
              "GRA Customs and the National AfCFTA Approval Committee.")
DECLARATIONS_FOR = {
    "ghana": {"appendix_iii_a"},
    "state_party": {"appendix_iii_a", "certificate_of_origin", "origin_declaration"},
}


class _Ctx:
    def __init__(self, rb):
        self.rb = rb
        self.findings = []
        self.trace = []
        self.fir = set()
        self.notes = []

    def find(self, severity, category, title, explanation, rule_ids, fix, input_ref=None, sub_reason=None):
        for rid in rule_ids:
            if rid not in self.rb["_index"]:
                raise KeyError(f"engine cites unknown rule id {rid}")
        self.findings.append(dict(id=f"F{len(self.findings) + 1}", severity=severity, category=category,
                                  title=title, input_ref=input_ref, explanation=explanation,
                                  rule_ids=list(rule_ids),
                                  provisions=[self.rb["_index"][r]["provision"] for r in rule_ids],
                                  fix=fix, sub_reason=sub_reason))
        if sub_reason:
            self.fir.add(sub_reason)

    def log(self, step, detail):
        self.trace.append({"step": step, "detail": detail})


def _status(field):
    return (field or {}).get("status", "missing") if isinstance(field, dict) else "missing"


def assess(case, rb, valuation_basis=None):
    ctx = _Ctx(rb)
    params = rb["parameters"]
    basis = valuation_basis or params["valuation_basis_default"]
    alt_basis = params["valuation_basis_alternative"] if basis == "customs_value" else "customs_value"
    tol_pct = Decimal(params["tolerance"]["percent"])
    sp_list = set(rb["state_parties"]["countries"])
    opmap = {m["code"]: m for m in rb["operation_map"]}
    product = case.get("product", {})
    inputs = case.get("inputs", [])

    result = {
        "engine_version": ENGINE_VERSION, "rulebase_version": rb["rulebase_version"],
        "case_id": case.get("case_id"), "valuation_basis": basis, "disclaimer": DISCLAIMER,
    }

    # ---- 1. Retrieval (deterministic, by heading) --------------------------------
    declared = product.get("declared_hs")
    head = heading_of(declared)
    ctx.log("retrieval", f"declared HS '{declared}' -> heading {head}")
    hs_conf = {"declared_hs": declared, "heading": head}
    if not declared or _status(product.get("declared_hs_field", {"status": "stated"})) not in USABLE:
        ctx.find("major", "hs", "Product HS code missing",
                 "The records do not give an HS code for the product. Without the code, the tool cannot find the rule.",
                 ["A2-10", "APPI-BOX-11"], "Ask the SME for the declared six-digit HS code of the product.",
                 sub_reason="missing")
        hs_conf["status"] = "missing"
        _form_checks(ctx, case, sp_list)
        return _finish(result, ctx, case, rb, None, None, None, hs_conf, basis, _food_aid(ctx, inputs))
    if head != rb["product_heading"]:
        ctx.find("major", "hs", "Product outside the rule base",
                 f"The declared code {declared} is not in heading 19.01. This tool has the rule for heading 19.01 only. It does not select another heading.",
                 ["APPIV-1901", "A2-6-2"], "The adviser checks the HS code. Products outside heading 19.01 are checked manually.",
                 sub_reason="out_of_rule_base")
        hs_conf["status"] = "out of rule base"
        _form_checks(ctx, case, sp_list)
        return _finish(result, ctx, case, rb, None, None, None, hs_conf, basis, _food_aid(ctx, inputs))
    if product.get("hs_doubt"):
        ctx.find("major", "hs", "Doubt whether the product belongs to heading 19.01",
                 "The product description does not clearly fit heading 19.01: "
                 + (product.get("hs_doubt_reason") or "reason not stated") + ". The tool does not select another heading.",
                 ["APPIV-1901", "APPIV-N2.1", "A2-10"],
                 "Adviser verifies the HS classification (blueprint: 'HS-code correct?'); re-run with the confirmed code.",
                 sub_reason="out_of_rule_base")
        hs_conf["status"] = "doubt flagged – routed to adviser"
        _form_checks(ctx, case, sp_list)
        return _finish(result, ctx, case, rb, None, None, None, hs_conf, basis, _food_aid(ctx, inputs))
    hs_conf["status"] = "declared 19.01, no doubt flagged (SME-declared, not verified)"
    ctx.log("retrieval", "rule APPIV-1901 retrieved; tolerance EXCL-AN-3 (draft) attached; Art. 7 attached")

    exw = money(case.get("ex_works_price"))
    exw_cur = (case.get("ex_works_price") or {}).get("currency") or params["currency"]

    # ---- 2. Classify inputs ------------------------------------------------------
    rows = []  # inputs relevant to the 19.01 rule
    cumulation_countries = set()
    for inp in inputs:
        iid, desc = inp.get("id"), inp.get("description", "")
        hs_ok = _status(inp.get("hs_field", {"status": "stated" if inp.get("hs_code") else "missing"})) in USABLE
        h = heading_of(inp.get("hs_code")) if hs_ok else None
        ch = chapter_of(inp.get("hs_code")) if hs_ok else None
        if inp.get("hs_doubt"):
            ctx.find("major", "hs", f"HS code of '{desc}' contradicts its description",
                     f"Line {iid} has HS code {inp.get('hs_code')}, but the description looks like a preparation of heading 19.01.",
                     ["APPIV-1901", "A2-10"], "Ask the supplier/SME to confirm the HS code of this input.",
                     input_ref=iid, sub_reason="contradictory")
            cat = "could_be_1901"
        elif not hs_ok or not inp.get("hs_code"):
            cat = "could_be_1901"
        elif h == "19.01":
            cat = "1901"
        else:
            cat = "other"
        if ch == "11" and "wheat" in desc.lower():
            ctx.notes.append({"rule_id": "APPIV-EXCH19", "input_ref": iid,
                              "text": "Information for the adviser: a Chapter 11 wheat input is present. The Ex-Chapter 19 condition "
                                      "('wheat Products of Chapter 11 used must be originating') is NOT applied (group decision); the 19.01 row governs."})

        origin = inp.get("origin_class") or "unknown"
        decl = inp.get("declaration") or {}
        decl_ok = bool(decl.get("present")) and decl.get("type") in DECLARATIONS_FOR.get(origin, set())
        country = inp.get("supplier_country")
        if origin == "state_party" and country not in sp_list:
            origin_res, why = "unresolved", f"supplier country '{country}' is not in the State Party list used (EX.CL draft decision para. 7)"
        elif origin in ("ghana", "state_party"):
            origin_res, why = ("originating", None) if decl_ok else ("unresolved", "no supplier declaration / proof of origin on file")
        elif origin == "non_state_party":
            origin_res, why = "non_originating", None
        else:
            origin_res, why = "unresolved", "origin not stated"

        conflicts = inp.get("conflicts") or []
        if cat == "other":
            # Not a 19.01 material: cannot breach the heading-change rule. Gaps are minor.
            if origin_res == "unresolved":
                ctx.find("minor", "origin_proof", f"Origin evidence incomplete for '{desc}'",
                         f"Line {iid}: {why}. The ingredient is not in heading 19.01, so this does not change the result. "
                         "The authority can ask for this proof.",
                         ["A2-22", "A2-31-2"], "Obtain a supplier declaration (Appendix III) or invoice showing origin.", input_ref=iid)
            for c in conflicts:
                ctx.find("minor", "consistency", f"Inconsistent {c.get('field')} for '{desc}'",
                         f"Line {iid}: the documents do not agree ({', '.join(map(str, c.get('values', [])))}).",
                         ["A2-22"], "Correct the documents so they agree.", input_ref=iid)
            continue

        # cat in ("1901", "could_be_1901")
        if origin_res == "originating":
            if origin == "state_party" and cat == "1901":
                cumulation_countries.add(country)
            ctx.log("inputs", f"{iid} '{desc}': {cat}, originating ({origin}) with {decl.get('type')} -> not counted")
            for c in conflicts:
                ctx.find("minor", "consistency", f"Inconsistent {c.get('field')} for '{desc}'",
                         f"Line {iid}: the documents do not agree.", ["A2-22"],
                         "Correct the documents so they agree.", input_ref=iid)
            continue
        if cat == "could_be_1901" and not inp.get("hs_doubt"):
            ctx.find("major", "hs", f"HS code missing or unreadable for '{desc}'",
                     f"Line {iid} has no proof of origin and its HS code is "
                     f"{'unreadable' if _status(inp.get('hs_field')) == 'unreadable' else 'missing'}. It can be an ingredient of heading 19.01.",
                     ["APPIV-1901", "A2-10"], "Ask the SME/supplier for the HS code of this input.",
                     input_ref=iid, sub_reason="missing")
        if origin_res == "unresolved":
            proof_rule = ["A2-31-1", "A2-8"] if origin == "state_party" else ["A2-21-3", "A2-APPIII-A"]
            ctx.find("major", "origin_proof", f"Origin of '{desc}' cannot be confirmed",
                     f"Line {iid} ({'heading 19.01' if cat == '1901' else 'possibly heading 19.01'}): {why}. "
                     "Without proof, the tool cannot count it as local.",
                     proof_rule, "Obtain the proof of origin (Certificate of Origin / Origin Declaration, or Appendix III supplier declaration).",
                     input_ref=iid, sub_reason="missing")
        for c in conflicts:
            ctx.find("major", "consistency", f"Contradictory {c.get('field')} for '{desc}'",
                     f"Line {iid}: the documents do not agree ({', '.join(map(str, c.get('values', [])))}). "
                     "The result depends on this ingredient. The tool cannot use the value until the SME clarifies it.",
                     ["APPIV-1901", "A2-22"], "Ask the SME which document is correct.", input_ref=iid, sub_reason="contradictory")
        rows.append(dict(inp=inp, cat=cat, origin_res=origin_res, conflicts=conflicts))

    # ---- 3. Tolerance calculation (exact) ---------------------------------------
    tol = _tolerance(ctx, rows, exw, exw_cur, tol_pct, basis, params)
    alt = _tolerance(_Ctx(rb), rows, exw, exw_cur, tol_pct, alt_basis, params, quiet=True)
    tol["alternative"] = {"basis": alt_basis, "status": alt["status"], "share_display": alt.get("share_display"),
                          "differs": alt["status"] != tol["status"]}
    rule = {"status": tol["status"], "rule_id": "APPIV-1901", "tolerance_rule_id": "EXCL-AN-3",
            "tolerance_legal_status": rb["_index"]["EXCL-AN-3"]["legal_status"]}
    if tol["status"] == "not met":
        ctx.find("critical", "rule_1901", "Imported heading 19.01 ingredients are above the 15% limit",
                 f"Imported ingredients of heading 19.01 are {tol['share_display']}% of the ex-works price. The limit is 15%. "
                 "The rule for heading 19.01 is not met.",
                 ["APPIV-1901", "EXCL-AN-3", "A2-1-y"],
                 "Source the 19.01 material(s) from Ghana or another State Party with proof of origin, or reduce their share to 15% or less.",
                 input_ref=",".join(tol["counted_ids"]))
    if tol["alternative"]["differs"] and tol["status"] in ("met", "met via 15% tolerance", "not met"):
        ctx.find("minor", "value", "Result depends on the valuation method",
                 f"Using {alt_basis.replace('_', ' ')} instead of {basis.replace('_', ' ')} gives '{alt['status']}'. "
                 "Annex 2 uses the customs value. The draft EX.CL text uses FOB.",
                 ["A2-1-y", "EXCL-AN-7"], "Adviser notes the valuation sensitivity when reviewing.")

    # ---- 4. Article 7(1) ----------------------------------------------------------
    art7 = _article7(ctx, case.get("production_steps") or [], opmap, rb)

    # ---- 5. Article 7(2) food aid --------------------------------------------------
    food = _food_aid(ctx, inputs)

    # ---- 6. Packaging and other evidence -----------------------------------------
    _form_checks(ctx, case, sp_list)
    if exw is None and not any(f["category"] == "rule_1901" or f["title"].startswith("Ex-works") for f in ctx.findings):
        ctx.find("minor", "form", "Ex-works price missing",
                 "The result does not need it here, but the application does.",
                 ["A2-1-k", "A2-22"], "Add the ex-works price.")

    return _finish(result, ctx, case, rb, rule, tol, art7, hs_conf, basis, food, cumulation_countries)


def _form_checks(ctx, case, sp_list):
    """Rule-independent packaging and Appendix I form checks (also run when out of rule base)."""
    for p in case.get("packaging") or []:
        if p.get("packing_type") == "retail" and p.get("origin_class") in (None, "unknown"):
            ctx.find("minor", "packaging", f"Origin of retail packing '{p.get('description')}' unknown",
                     "Retail packing counts as a material. It is not in heading 19.01, so it does not change the result. "
                     "Keep its invoice: the importing country can check the packing separately.",
                     ["A2-11-3", "A2-11-1", "APPIV-1901"], "Keep the packaging supplier invoice on file.", input_ref=p.get("id"))
    exp = case.get("exporter") or {}
    if not exp.get("registration_no"):
        ctx.find("minor", "form", "Exporter registration number missing",
                 "The certificate form (Box 1) asks for the exporter registration number.",
                 ["APPI-BOX-1"], "Add the exporter registration number.")
    cons = case.get("consignee") or {}
    dest = cons.get("country") or case.get("destination_country")
    if not cons.get("name") or not dest:
        ctx.find("minor", "form", "Consignee or destination missing",
                 "The certificate form (Box 2) needs the name and address of the consignee.",
                 ["APPI-BOX-2"], "Add consignee name, address and destination country.")
    elif dest not in sp_list:
        ctx.find("minor", "form", "Destination not in the State Party list used",
                 f"{dest} is not in the list of AfCFTA State Parties used by this tool (January 2022). The tool does not check destinations.",
                 ["APPI-BOX-2", "EXCL-DD-7"], "The adviser checks the destination country.")


def _food_aid(ctx, inputs):
    """Art. 7(2) applies 'notwithstanding any provision of this Annex' – independent of the HS heading."""
    food = {"status": "no food-aid input declared"}
    aid = [i for i in inputs if i.get("food_aid") is True]
    if aid:
        food["status"] = "food-aid input present"
        for i in aid:
            ctx.find("critical", "food_aid", f"Input '{i.get('description')}' comes from food aid",
                     "A product made fully or partly from food aid is not originating. "
                     "The product fails.",
                     ["A2-7-2"], "Replace the food-aid input with a commercially purchased input and keep the purchase records.",
                     input_ref=i.get("id"))
    elif any(i.get("food_aid") is None for i in inputs):
        food["status"] = "not confirmed for all inputs"
        ctx.find("minor", "food_aid", "Food-aid status not confirmed",
                 "The records do not say if an ingredient comes from food aid.",
                 ["A2-7-2"], "SME confirms in writing that no input was obtained from food aid.")
    return food


def _tolerance(ctx, rows, exw, exw_cur, tol_pct, basis, params, quiet=False):
    field = "customs_value" if basis == "customs_value" else "fob_value"
    counted, unresolved, total = [], [], Decimal(0)
    for row in rows:
        inp = row["inp"]
        if row["origin_res"] == "unresolved" or row["cat"] == "could_be_1901" or row["conflicts"]:
            unresolved.append(inp.get("id"))  # not counted; outcome stays open unless the known sum already exceeds 15%
            continue
        val, used = money(inp.get(field)), field
        if val is None and basis == "customs_value":
            val, used = money(inp.get("first_ascertainable_price")), "first_ascertainable_price"
        cur = (inp.get(field) or inp.get("first_ascertainable_price") or {}).get("currency") or params["currency"]
        if val is not None and cur != exw_cur:
            if not quiet:
                ctx.find("major", "value", f"Currency mismatch for '{inp.get('description')}'",
                         f"The value is in {cur}, but the ex-works price is in {exw_cur}. The tool does not convert currencies.",
                         ["A2-1-y"], "Ask the SME for the value in GHS as declared to Customs.",
                         input_ref=inp.get("id"), sub_reason="contradictory")
            if inp.get("id") not in unresolved:
                unresolved.append(inp.get("id"))
            continue
        if val is None:
            if not quiet:
                ctx.find("major", "value", f"Value missing or unreadable for '{inp.get('description')}'",
                         f"Line {inp.get('id')} is an imported ingredient of heading 19.01. The 15% calculation needs its value. "
                         "The tool does not use zero for a missing value.",
                         ["A2-1-y", "EXCL-AN-3"], "Ask the SME for the customs entry / invoice showing this value.",
                         input_ref=inp.get("id"), sub_reason="missing")
            if inp.get("id") not in unresolved:
                unresolved.append(inp.get("id"))
            continue
        if used == "first_ascertainable_price" and not quiet:
            ctx.find("minor", "value", f"Fallback price used for '{inp.get('description')}'",
                     "The customs value is not known. The tool uses the first price paid in a State Party.",
                     ["A2-1-y"], "Confirm the Customs Value if available.", input_ref=inp.get("id"))
        if (inp.get(field) or {}).get("status") == "inferred" and not quiet:
            ctx.find("minor", "value", f"Value of '{inp.get('description')}' is inferred",
                     "The value is derived. It is not read directly from a document.", ["A2-22"],
                     "Adviser checks the value against the source document.", input_ref=inp.get("id"))
        counted.append({"input_id": inp.get("id"), "description": inp.get("description"),
                        "value": str(val), "value_field": used, "currency": cur})
        total += val

    out = {"basis": basis, "items": counted, "counted_ids": [c["input_id"] for c in counted],
           "unresolved_ids": unresolved, "total": str(total), "limit_percent": str(tol_pct),
           "ex_works_price": str(exw) if exw is not None else None, "currency": exw_cur}
    if exw is None or exw <= 0:
        if counted or unresolved:
            out["status"] = "unclear"
            if not quiet:
                ctx.find("major", "value", "Ex-works price missing",
                         "The 15% calculation needs the ex-works price.", ["A2-1-k", "EXCL-AN-3"],
                         "Ask the SME for the ex-works price of the product.", sub_reason="missing")
        else:
            out.update(status="met", share_display="0.00", margin_pp_display="15.00",
                       explanation="No non-originating heading 19.01 material: the heading-change rule is met without the tolerance.")
        return out
    lhs, rhs = total * 100, tol_pct * exw  # exact comparison: total*100 <= 15*exw
    share = total * 100 / exw
    out.update(share_display=fmt(share, "0.001"), margin_pp_display=fmt(tol_pct - share, "0.001"),
               comparison=f"{total} × 100 = {lhs}  vs  {tol_pct} × {exw} = {rhs}",
               within_limit=lhs <= rhs, share_fraction=f"{total} / {exw}",
               headroom=str((tol_pct * exw / 100 - total).quantize(Decimal("0.01"))))
    if lhs > rhs:
        out["status"] = "not met"  # determinate even if other inputs are unresolved (GD-Q5)
    elif unresolved:
        out["status"] = "unclear"
        out["share_is_lower_bound"] = True  # only the known part; unresolved inputs are not counted
    elif total == 0:
        out["status"] = "met"
    else:
        out["status"] = "met via 15% tolerance"
    if not quiet:
        ctx.log("tolerance", f"basis={basis}; {out['comparison']}; status={out['status']}")
    return out


def _article7(ctx, steps, opmap, rb):
    out = {"steps": [], "status": None}
    if not steps:
        ctx.find("major", "process", "Production process not described",
                 "The tool must check the production steps in every case. The records do not describe them.",
                 ["A2-7-1", "A2-22"], "Ask the SME for a step-by-step description of production and where each step happens.",
                 sub_reason="missing")
        out["status"] = "unclear"
        return out
    substantive_gh, substantive_abroad, unclear, letters = [], [], [], []
    for s in steps:
        m = opmap.get(s.get("operation_code") or "")
        st = m["status"] if m else "unclear"
        out["steps"].append({"id": s.get("id"), "description": s.get("description"), "operation_code": s.get("operation_code"),
                             "map_status": st, "art7_letter": m.get("art7_letter") if m else None,
                             "location": s.get("location_country")})
        if st == "not_listed":
            (substantive_gh if s.get("location_country") == "Ghana" else substantive_abroad).append(s)
        elif st == "unclear":
            unclear.append(s)
        else:
            letters.append(m["art7_letter"])
    if substantive_gh:
        out["status"] = "met"
        out["explanation"] = ("At least one step carried out in Ghana is not an Article 7(1) operation "
                              "(group interpretation of the operation map).")
    elif unclear:
        out["status"] = "unclear"
        for s in unclear:
            ctx.find("major", "process", f"Process step '{s.get('description')}' is unclear",
                     "The description does not show if this is a simple operation.",
                     ["A2-7-1", "A2-7-3"], "Ask the SME what equipment and skills the step uses and what it changes in the product.",
                     input_ref=s.get("id"), sub_reason="missing")
    elif substantive_abroad:
        out["status"] = "unclear"
        ctx.find("major", "process", "The main processing is not done in Ghana",
                 "The steps that are more than simple operations are not done in Ghana.",
                 ["A2-8", "A2-7-1"], "Adviser checks where the last substantive working takes place.",
                 sub_reason="missing")
    else:
        out["status"] = "not met"
        uniq = sorted(set(letters))
        rid = ["A2-7-1"] + [f"A2-7-1-{x}" for x in uniq] + (["A2-7-1-o"] if len(uniq) > 1 else [])
        ctx.find("critical", "article7", "Only simple operations in production",
                 "All production steps are simple operations listed in Article 7(1). "
                 "Simple operations do not give origin, even when the rule for heading 19.01 is met.",
                 rid, "The adviser discusses with the SME if more processing in Ghana is possible.")
    ctx.log("article7", f"status={out['status']}")
    return out


def _finish(result, ctx, case, rb, rule, tol, art7, hs_conf, basis, food=None, cumulation=None):
    crit = [f for f in ctx.findings if f["severity"] == "critical"]
    if crit:
        outcome = {"label": UNLIKELY, "sub_reasons": []}
    elif ctx.fir:
        order = ["out_of_rule_base", "contradictory", "missing"]
        outcome = {"label": FIR, "sub_reasons": [r for r in order if r in ctx.fir]}
    else:
        outcome = {"label": LIKELY, "sub_reasons": []}
    ctx.findings.sort(key=lambda f: (SEV_ORDER[f["severity"]], CAT_ORDER.get(f["category"], 99)))
    for i, f in enumerate(ctx.findings):
        f["id"] = f"F{i + 1}"
        f["sme_action"] = _sme_action(f)
    rel_major = [f for f in ctx.findings if f["severity"] in ("critical", "major")]
    evidence = {"status": "complete for the 19.01 rule" if not [f for f in ctx.findings if f["sub_reason"]] else "gaps affect the result",
                "critical": len(crit), "major": len([f for f in ctx.findings if f["severity"] == "major"]),
                "minor": len([f for f in ctx.findings if f["severity"] == "minor"])}
    result.update(
        outcome=outcome,
        components={"rule_1901": rule or {"status": "not assessed"},
                    "tolerance": tol or {"status": "not assessed"},
                    "article7": art7 or {"status": "not assessed"},
                    "food_aid": food or {"status": "not assessed"},
                    "evidence": evidence, "hs_confidence": hs_conf},
        findings=ctx.findings, notes=ctx.notes, trace=ctx.trace,
        requirements=_requirements(rule, tol, art7, food, hs_conf, ctx, case),
        missing_info_request=_request(case, ctx.findings),
    )
    result["folder"] = build_folder(case, result, rb, sorted(cumulation or []))
    return result


def _pct(x):
    """'14.900' -> '14.9' (display only)."""
    if x is None:
        return "—"
    t = str(x).rstrip("0").rstrip(".")
    return t if t not in ("", "-") else "0"


def _ghs(x, cur="GHS"):
    try:
        return f"{cur} {Decimal(str(x)):,.2f}"
    except Exception:
        return f"{cur} {x}"


SME_ACTIONS = [  # (category, title prefix) -> action addressed to the SME (used in the SME report)
    ("rule_1901", "", "Buy the heading 19.01 ingredient from Ghana or another AfCFTA country with proof of origin, or reduce its value to 15% of the ex-works price or less."),
    ("article7", "", "Add processing in Ghana that is more than mixing, grinding or packing (for example cooking or drying), or discuss your plan with the adviser."),
    ("food_aid", "Input", "Replace the food-aid ingredient with a purchased ingredient and keep the purchase records."),
    ("food_aid", "Food-aid status", "Confirm in writing that no ingredient comes from food aid."),
    ("hs", "Product HS code missing", "Send the HS code of your product."),
    ("hs", "Product outside", "Talk to the adviser about the HS code of your product."),
    ("hs", "Doubt whether", "Confirm the HS code of your product with the adviser and send a full product description."),
    ("hs", "HS code missing", "Send the HS code of {input} from the supplier invoice."),
    ("hs", "HS code of", "Ask your supplier to confirm the HS code of {input}."),
    ("origin_proof", "", "Send the supplier declaration or certificate of origin for {input}."),
    ("value", "Value missing", "Send the customs entry or supplier invoice that shows the value of {input}."),
    ("value", "Currency", "Send the value of {input} in GHS, as declared to Customs."),
    ("value", "Ex-works price missing", "Send the ex-works price of the product."),
    ("consistency", "", "Check which document is correct for {input} and send a corrected copy."),
    ("process", "", "Describe this production step: the equipment you use and what it changes in the product."),
]


def _sme_action(f):
    for cat, prefix, text in SME_ACTIONS:
        if f["category"] == cat and f["title"].startswith(prefix):
            m = re.search(r"'([^']+)'", f["title"])
            return text.replace("{input}", m.group(1).lower() if m else "this ingredient")
    return None


def _names(items):
    items = [i for i in items if i]
    return ", ".join(items[:-1]) + (" and " if len(items) > 1 else "") + items[-1] if items else ""


def _requirements(rule, tol, art7, food, hs_conf, ctx, case):
    """Requirement-by-requirement check in plain language (adviser view and SME report)."""
    prod = case.get("product") or {}
    desc = prod.get("description") or "no description"
    st = hs_conf.get("status", "")
    if st.startswith("declared 19.01"):
        ev, s1 = f"The declared HS code is {hs_conf.get('declared_hs')}. The product description fits heading 19.01: “{desc}”.", "met"
    elif st == "missing":
        ev, s1 = "The records do not give an HS code for the product.", "unclear"
    elif st == "out of rule base":
        ev, s1 = f"The declared code {hs_conf.get('declared_hs')} is not in heading 19.01. This tool covers heading 19.01 only.", "unclear"
    else:
        ev, s1 = f"The declared HS code is {hs_conf.get('declared_hs')}, but the description “{desc}” does not clearly fit heading 19.01.", "unclear"
    rows = [{"requirement": "The product is in HS heading 19.01.", "evidence": ev, "status": s1,
             "source": "Appendix IV, heading 19.01", "rule_ids": ["APPIV-1901", "A2-10"]}]
    if not rule:
        rows.append({"requirement": "No ingredient comes from food aid.", "evidence": _food_text(food), "status": _food_status(food),
                     "source": "Annex 2, Art. 7(2)", "rule_ids": ["A2-7-2"]})
        return rows
    inputs = {i.get("id"): i for i in case.get("inputs") or []}
    if tol["status"] == "met":
        ev2 = "No imported ingredient is classified in heading 19.01."
    elif tol["status"] == "unclear":
        names = _names([inputs.get(i, {}).get("description") for i in tol.get("unresolved_ids", [])])
        ev2 = (f"{names} may be an imported ingredient of heading 19.01. The value, HS code or origin is missing or the documents do not agree. "
               "The share cannot be calculated yet.") if names else "The ex-works price is missing. The share cannot be calculated yet."
    else:
        names = _names([i["description"] for i in tol["items"]])
        n = len(tol["items"])
        ev2 = (f"{'One imported ingredient is' if n == 1 else f'{n} imported ingredients are'} in heading 19.01: {names}, "
               f"value {_ghs(tol['total'], tol['currency'])}. This is {_pct(tol['share_display'])}% of the ex-works price of {_ghs(tol['ex_works_price'], tol['currency'])}. "
               f"The limit is {tol['limit_percent']}%.")
    rows.append({"requirement": f"Imported ingredients of heading 19.01 are at most {tol['limit_percent']}% of the ex-works price.",
                 "evidence": ev2, "status": {"met": "met", "met via 15% tolerance": "met", "not met": "not met"}.get(tol["status"], "unclear"),
                 "source": "Appendix IV, heading 19.01; EX.CL/1329 annex (draft)", "rule_ids": ["APPIV-1901", "EXCL-AN-3"]})
    steps = art7.get("steps", [])
    sub = [s["description"].lower() for s in steps if s["map_status"] == "not_listed"]
    simple = [s["description"].lower() for s in steps if s["map_status"] == "listed"]
    vague = [s["description"].lower() for s in steps if s["map_status"] == "unclear"]
    if art7["status"] == "met":
        ev3 = f"These steps in Ghana are more than simple operations: {_names(sub)}."
    elif art7["status"] == "not met":
        ev3 = f"All steps are simple operations: {_names(simple)}. Simple operations alone do not give origin."
    elif vague:
        ev3 = f"The description of this step is not clear enough: {_names(vague)}."
    elif not steps:
        ev3 = "The records do not describe the production steps."
    else:
        ev3 = "The steps that are more than simple operations are not done in Ghana."
    rows.append({"requirement": "The work done in Ghana is more than simple operations such as mixing or packing.", "evidence": ev3,
                 "status": art7["status"], "source": "Annex 2, Art. 7", "rule_ids": ["A2-7-1", "A2-7-3"]})
    rows.append({"requirement": "No ingredient comes from food aid.", "evidence": _food_text(food), "status": _food_status(food),
                 "source": "Annex 2, Art. 7(2)", "rule_ids": ["A2-7-2"]})
    local = [i for i in inputs.values() if i.get("origin_class") in ("ghana", "state_party")]
    proof = [i for i in local if (i.get("declaration") or {}).get("present")]
    major_proof = any(f["category"] == "origin_proof" and f["severity"] == "major" for f in ctx.findings)
    ev5 = (f"Supplier declarations or certificates are on file for {len(proof)} of {len(local)} ingredients from Ghana or other AfCFTA countries."
           if local else "No ingredient comes from Ghana or another AfCFTA country.")
    if major_proof:
        ev5 += " Proof is missing for an ingredient that the result depends on."
    rows.append({"requirement": "There is proof of origin for local and AfCFTA ingredients.", "evidence": ev5,
                 "status": "unclear" if major_proof else "met", "source": "Annex 2, Art. 31 and Appendix III", "rule_ids": ["A2-31-1", "A2-APPIII-A"]})
    return rows


def _food_text(food):
    return {"no food-aid input declared": "The production notes state that no ingredient comes from food aid.",
            "food-aid input present": "The records state that an ingredient comes from food aid.",
            "not confirmed for all inputs": "The records do not say if an ingredient comes from food aid."}.get((food or {}).get("status"), "Not checked.")


def _food_status(food):
    return {"no food-aid input declared": "met", "food-aid input present": "not met"}.get((food or {}).get("status"), "unclear")


def _request(case, findings):
    need = [f for f in findings if f["sub_reason"] in ("missing", "contradictory")]
    if not need:
        return None
    name = (case.get("exporter") or {}).get("name") or "the exporter"
    lines = [f"Dear {name},", "",
             "Thank you for your documents. To complete the pre-check, please send us the items below:"]
    for i, f in enumerate(need, 1):
        lines.append(f"{i}. {f.get('sme_action') or f['fix']}")
    lines += ["", "The pre-check is indicative only. GRA Customs and the National AfCFTA Approval Committee make the official decision.",
              "Kind regards,", "Trade adviser, AI Adoption and Innovation Centre"]
    return "\n".join(lines)
