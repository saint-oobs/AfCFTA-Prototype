"""STUB – synthetic transcription.

Stands in for the multimodal language model in pipeline stages 2–3. It reads the TEXT LAYER of the
synthetic documents (it cannot read images) and extracts the fixed schema with simple rules and a
small EN/FR glossary. Every field is tagged stated / inferred / missing / unreadable with a source
snippet. It never guesses a value: '[illegible]' stays unreadable.
"""
import re

LABEL = "Prototype transcription (synthetic documents)"
STUB_VERSION = "1.2.0"  # 1.2.0: SME summary in plain language; product description snippets for the adviser
# 1.1.0  # 1.1.0: supplier documents matched by supplier name + goods (revision R1)
ILL = "[illegible]"

FR_GOODS = {"malt, non torréfié": "Malt, not roasted", "sirop de glucose": "Glucose syrup", "mil en grains": "Millet grain",
            "fèves de soja": "Soya beans", "sucre de canne": "Cane sugar", "lait écrémé en poudre": "Skimmed milk powder",
            "extrait de malt concentré": "Malt extract concentrate", "prémélange céréalier préparé": "Cereal-based premix preparation",
            "farine de blé": "Wheat flour", "levure chimique": "Baking powder", "prémélange de boulangerie préparé": "Bakery premix preparation"}
UNITS = {"kg": "kg", "kgs": "kg", "kilos": "kg", "kilo": "kg", "bags": "bags", "sacs": "bags", "jars": "jars", "pouches": "pouches"}
CURRENCIES = {"GHS": "GHS", "GH₵": "GHS", "GHC": "GHS", "GHc": "GHS", "Ghc": "GHS", "EUR": "EUR", "USD": "USD"}
ORIGIN = {"ghana": "ghana", "afcfta state party": "state_party", "imported (non-state party)": "non_state_party"}
OPS = [  # (keywords EN/FR, operation code) – the AI task 'classify process step into fixed taxonomy'
    (("mashing", "brassage"), "mashing_enzymatic"), (("evaporation", "évaporation"), "evaporation_concentration"),
    (("roasting", "torréfaction"), "roasting_toasting"), (("extrusion",), "cooking_extrusion"),
    (("drum drying", "séchage sur cylindre"), "drying_drum_spray"), (("simple grinding", "simple broyage"), "simple_grinding"),
    (("simple mixing", "simple mélange"), "simple_mixing"), (("simple sifting", "simple tamisage"), "simple_sifting_sorting"), (("cleaning", "nettoyage"), "cleaning_washing"),
    (("filling", "remplissage", "mise en sachets"), "simple_packaging"), (("labelling", "étiquetage"), "labelling"),
    (("fermentation",), "fermentation"),
]
FR_STEPS = {  # translation of French production notes (the live model translates freely)
    "brassage du malt à l'eau chaude": "Mashing of malt with hot water", "filtration et évaporation sous vide": "Filtration and vacuum evaporation",
    "remplissage des pots": "Filling into jars", "étiquetage": "Labelling", "nettoyage du mil": "Cleaning of millet",
    "torréfaction du mil et du soja": "Roasting of millet and soya", "cuisson par extrusion": "Cooking by extrusion",
    "séchage sur cylindre de la pâte cuite": "Drum drying of the cooked paste", "simple broyage": "Simple grinding",
    "simple mélange avec sucre et lait en poudre": "Simple mixing with sugar and milk powder",
    "simple mélange avec lait en poudre et sucre": "Simple mixing with milk powder and sugar", "mise en sachets": "Filling into bags",
    "remplissage des boîtes": "Filling into cartons", "simple tamisage de la farine": "Simple sifting of flour",
    "séchage sur cylindre de l'extrait de malt avec une partie de la farine": "Drum drying of the malt extract with part of the flour",
    "simple mélange avec farine, sucre et levure chimique": "Simple mixing with flour, sugar and baking powder",
    "le produit est traité à l'usine": "Product is processed at the factory",
    "simple mélange d'extrait de malt acheté et de sirop de glucose": "Simple mixing of purchased malt extract with glucose syrup",
}
PRODUCT_CUES = ("malt extract", "preparation", "mix", "precooked", "porridge", "préparation", "mélange")
DOUBT_CUES = ("only", "no other ingredient", "seul")
INPUT_1901_CUES = ("malt extract", "extrait de malt", "premix", "prémélange", "preparation")
DECL_TITLES = [("appendix iii", "appendix_iii_a"), ("déclaration du fournisseur", "appendix_iii_a"),
               ("certificate of origin", "certificate_of_origin"), ("certificat d'origine", "certificate_of_origin"),
               ("supplier invoice", "supplier_invoice"), ("facture du fournisseur", "supplier_invoice")]


def _num(s):
    s = (s or "").strip()
    if not s or s in ("—", "-"):
        return None, "missing"
    if ILL in s:
        return None, "unreadable"
    s2 = s.replace(",", "")
    return (s2, "stated") if re.fullmatch(r"\d+(\.\d+)?", s2) else (None, "unreadable")


def _kv(text):
    out = {}
    for line in text.split("\n"):
        m = re.match(r"\s*([^:|]+?)\s*:\s*(.*)$", line)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def transcribe(documents):
    tags = []

    def tag(path, status, snippet, doc_id):
        tags.append({"field": path, "status": status, "snippet": snippet, "doc_id": doc_id})

    case = {"synthetic": True, "exporter": {}, "consignee": {}, "product": {}, "inputs": [], "production_steps": [],
            "packaging": [], "invoice": {}, "ex_works_price": {"amount": None, "currency": "GHS", "status": "missing"}}
    by_type = {}
    for d in documents:
        by_type.setdefault(d["type"], []).append(d)

    for d in by_type.get("exporter_profile", []):
        kv = _kv(d["text"])
        case["exporter"] = {"name": kv.get("name"), "address": kv.get("address"), "registration_no": kv.get("registration no") or None}
        tag("exporter.registration_no", "stated" if case["exporter"]["registration_no"] else "missing", kv.get("registration no", ""), d["doc_id"])

    for d in by_type.get("bill_of_materials", []):
        kv = _kv(d["text"])
        case["product"].update(description=kv.get("product"), declared_hs=kv.get("declared hs"))
        tag("product.declared_hs", "stated" if kv.get("declared hs") else "missing", f"Declared HS: {kv.get('declared hs')}", d["doc_id"])
        tag("product.description", "stated" if kv.get("product") else "missing", f"Product: {kv.get('product')}", d["doc_id"])
        section = None
        for line in d["text"].split("\n"):
            if line.startswith("ID |"):
                section = "inputs"; continue
            if line.strip() == "PACKAGING":
                section = "packaging"; continue
            cols = [c.strip() for c in line.split("|")]
            if section == "inputs" and len(cols) == 11:
                iid, desc, qty, unit, cv, fob, cur, sup, ctry, hs, org = cols
                cur_n = CURRENCIES.get(cur, cur)
                cvv, cvs = _num(cv); fv, fs = _num(fob); qv, qs = _num(qty)
                inp = {"id": iid, "description": desc, "quantity": {"value": qv, "unit": UNITS.get(unit.lower(), unit)},
                       "customs_value": {"amount": cvv, "currency": cur_n, "status": cvs},
                       "fob_value": {"amount": fv, "currency": cur_n, "status": fs},
                       "supplier": sup, "supplier_country": None if ctry in ("—", "") else ctry,
                       "origin_class": ORIGIN.get(org.lower(), "unknown"),
                       "hs_code": None if hs in ("—", "") else hs,
                       "hs_field": {"status": "missing" if hs in ("—", "") else ("unreadable" if ILL in hs else "stated")},
                       "declaration": {"type": None, "present": False}, "conflicts": [], "food_aid": None}
                low = desc.lower()
                from_heading = re.sub(r"\D", "", hs or "")[:4]
                if any(c in low for c in INPUT_1901_CUES) and from_heading != "1901":
                    inp["hs_doubt"] = True
                    tag(f"{iid}.hs_code", "inferred", f"description '{desc}' suggests heading 19.01 but coded {hs}", d["doc_id"])
                for f, st, sn in (("customs_value", cvs, cv), ("fob_value", fs, fob), ("hs_code", inp["hs_field"]["status"], hs),
                                  ("origin_class", "missing" if inp["origin_class"] == "unknown" else "stated", org)):
                    tag(f"{iid}.{f}", st, f"{iid} | {desc} | … {sn}", d["doc_id"])
                case["inputs"].append(inp)
            elif section == "packaging" and len(cols) == 5:
                pid, desc, ptype, hs, ctry = cols
                case["packaging"].append({"id": pid, "description": desc, "packing_type": ptype, "hs_code": hs,
                                          "origin_class": "ghana" if ctry == "Ghana" else ("unknown" if ctry in ("—", "") else "other")})
                tag(f"{pid}.origin", "missing" if ctry in ("—", "") else "stated", line, d["doc_id"])

    def match(goods_en, supplier):
        # R1 (adapter 1.1.0): two BOM lines can share a description (e.g. two lots of malt extract
        # concentrate). Match on supplier name AND goods; fall back to goods only if unique.
        cands = [i for i in case["inputs"] if i["description"].lower() == goods_en.lower()]
        exact = [i for i in cands if (i.get("supplier") or "").lower() == (supplier or "").lower()]
        if len(exact) == 1:
            return exact[0]
        return cands[0] if len(cands) == 1 else None
    for typ in ("appendix_iii_a", "certificate_of_origin", "supplier_invoice"):
        for d in by_type.get(typ, []):
            kv = _kv(d["text"])
            title = " ".join(d["text"].split("\n")[:2]).lower()
            dtype = next((v for k, v in DECL_TITLES if k in title), None)
            goods = kv.get("goods") or kv.get("marchandises") or ""
            goods_en = FR_GOODS.get(goods.lower(), goods)
            inp = match(goods_en, kv.get("supplier") or kv.get("fournisseur"))
            if not inp:
                tag("supplier_document", "unmatched (ambiguous or unknown goods)", goods, d["doc_id"]); continue
            inp["declaration"] = {"type": dtype, "present": True}
            tag(f"{inp['id']}.declaration", "stated", d["text"].split("\n")[1], d["doc_id"])
            q = kv.get("quantity") or kv.get("quantité") or ""
            m = re.match(r"([\d.,]+)\s*(\S+)", q)
            if m and inp["quantity"]["value"]:
                qv, qu = m.group(1).replace(",", ""), UNITS.get(m.group(2).lower(), m.group(2))
                if (qv, qu) != (inp["quantity"]["value"], inp["quantity"]["unit"]):
                    inp["conflicts"].append({"field": "quantity", "values": [f"{inp['quantity']['value']} {inp['quantity']['unit']} (BOM)", f"{qv} {qu} ({d['doc_id']})"],
                                             "sources": ["DOC-BOM", d["doc_id"]], "note": "quantity/unit differs between BOM and supplier document"})
            v = kv.get("customs value") or kv.get("valeur en douane") or kv.get("invoice value") or kv.get("valeur facturée") or ""
            vm = re.match(r"(\S+)\s*(\S+)?", v)
            if vm:
                val, st = _num(vm.group(1))
                cv = inp["customs_value"]
                if st == "stated" and cv["status"] == "stated" and val != cv["amount"] and \
                        abs(float(val) - float(cv["amount"])) > 0.005:
                    inp["conflicts"].append({"field": "customs_value", "values": [f"{cv['amount']} (BOM)", f"{val} ({d['doc_id']})"],
                                             "sources": ["DOC-BOM", d["doc_id"]], "note": "value differs between BOM and supplier invoice"})
                elif st == "stated" and cv["status"] in ("missing", "unreadable"):
                    inp["customs_value"] = {"amount": val, "currency": CURRENCIES.get(vm.group(2) or "GHS", "GHS"), "status": "stated"}
                    tag(f"{inp['id']}.customs_value", "stated", f"recovered from {d['doc_id']}: {v}", d["doc_id"])

    for d in by_type.get("production_notes", []):
        for line in d["text"].split("\n")[1:]:
            m = re.match(r"\s*(\d+)\.\s*(.+?)\s+–\s+[^,]+,\s*(.+)$", line)
            if m:
                text = m.group(2); low = text.lower()
                if low in FR_STEPS:
                    text = FR_STEPS[low]; tag(f"S{m.group(1)}.description", "inferred", f"translated from French: {m.group(2)}", d["doc_id"])
                code = next((c for kws, c in OPS if any(k in low for k in kws)), "unspecified_processing")
                case["production_steps"].append({"id": f"S{m.group(1)}", "description": text, "operation_code": code,
                                                 "location_country": m.group(3).strip(), "status": "inferred"})
                tag(f"S{m.group(1)}.operation_code", "inferred", line, d["doc_id"])
            elif line.lower().startswith(("food aid", "aide alimentaire")):
                low = line.lower()
                if "none" in low or "aucun" in low:
                    for i in case["inputs"]:
                        i["food_aid"] = False
                else:
                    for i in case["inputs"]:
                        i["food_aid"] = i["description"].lower() in low
                tag("inputs.food_aid", "stated", line, d["doc_id"])

    for d in by_type.get("costing_sheet", []):
        m = re.search(r"Ex-works price[^:]*:\s*([\d,.]+|\[illegible\])\s*(\S+)?", d["text"])
        if m:
            val, st = _num(m.group(1))
            case["ex_works_price"] = {"amount": val, "currency": CURRENCIES.get(m.group(2) or "GHS", "GHS"), "status": st}
            tag("ex_works_price", st, m.group(0), d["doc_id"])

    for d in by_type.get("export_invoice", []):
        kv = _kv(d["text"])
        tag("product.description", "stated" if kv.get("goods") else "missing", f"Goods: {kv.get('goods')}", d["doc_id"])
        case["consignee"] = {"name": kv.get("consignee"), "address": kv.get("consignee address"), "country": kv.get("destination")}
        case["destination_country"] = kv.get("destination")
        val = (kv.get("value") or "").split(" ")
        case["invoice"] = {"number": kv.get("invoice no"), "date": kv.get("date"), "value": val[0] if val else None,
                           "currency": val[1] if len(val) > 1 else None, "incoterm": kv.get("incoterm")}
        q = (kv.get("quantity") or "").split(" ")
        case["product"].update(quantity=q[0] if q else None, unit=q[1] if len(q) > 1 else None,
                               gross_weight_kg=(kv.get("gross weight") or "").replace(" kg", "") or None,
                               marks=kv.get("marks"), packaging_count=kv.get("packages"), transport=kv.get("transport"),
                               statistical_measure=kv.get("gross weight"))

    # HS-plausibility support for the product (never picks another heading)
    desc = (case["product"].get("description") or "").lower()
    if desc and (not any(c in desc for c in PRODUCT_CUES) or any(c in desc for c in DOUBT_CUES)):
        case["product"]["hs_doubt"] = True
        case["product"]["hs_doubt_reason"] = "the description reads like a single ground cereal, not a food preparation"
        tag("product.declared_hs", "inferred", "HS plausibility: doubt", "DOC-BOM")
    return {"mode": "stub", "label": LABEL, "adapter_version": STUB_VERSION, "case": case, "field_tags": tags}


def explain(result):
    """SME summary in plain language (stub = template; a live model may rephrase it).
    Only facts from the engine result. No rule ids: it is a summary for the SME."""
    o = result["outcome"]
    t = result["components"]["tolerance"]
    reqs = result.get("requirements", [])
    head = {"Likely to qualify": "Your product is likely to meet the AfCFTA rules of origin.",
            "Likely not to qualify": "Your product is likely NOT to meet the AfCFTA rules of origin.",
            "Further information required": "We cannot give a result yet. We need more information from you."}[o["label"]]
    lines = [head, ""]
    bad = [r for r in reqs if r["status"] in ("not met", "unclear")]
    good = [r for r in reqs if r["status"] == "met"]
    if bad:
        lines.append("Main reasons:")
        lines += [f"- {r['evidence']}" for r in bad[:3]]
    else:
        lines.append("Main reasons:")
        lines += [f"- {r['evidence']}" for r in good[1:3]]
    if t.get("status") == "met via 15% tolerance":
        margin = str(t['margin_pp_display']).rstrip("0").rstrip(".") or "0"
        lines += ["", f"Note: the 15% limit is the AfCFTA tolerance rule (EX.CL/1329(XL), Annex, item 3). Your margin is {margin} percentage points. "
                      "A change in prices or recipe can change the result."]
    fixes = list(dict.fromkeys(f.get("sme_action") or f["fix"] for f in result["findings"] if f["severity"] in ("critical", "major")))[:3]
    lines += ["", "What to do next:"]
    lines += [f"- {x}" for x in fixes] if fixes else ["- Keep your supplier declarations, invoices and production records together."]
    lines.append("- You decide whether to apply. GRA Customs and the National AfCFTA Approval Committee make the official decision.")
    return "\n".join(lines)
