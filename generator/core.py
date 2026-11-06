"""Seeded synthetic SME case generator (heading 19.01 only). Same seed + spec -> same case.

Output per case:
  truth      – clean structured record (engine input schema) = ground truth
  documents  – the synthetic records an SME would hand in (text layer; some rendered as images)
  meta       – spec, injected defects, generator version, seed
The generator never imports the engine or the answer key and never computes an outcome.
"""
import json
import pathlib
import random
from decimal import Decimal, ROUND_HALF_UP

from .recipes import (RECIPES, EU_SUPPLIERS, BUYER_FIRST, BUYER_SECOND, SUPPLIER_NAMES, EQUIPMENT, STATE_PARTY_SUPPLIERS, NON_STATE_PARTY_SUPPLIERS, FRANCOPHONE, AMBIGUOUS_STEP,
                      FIRST, SECOND, TOWNS, CONSIGNEE_CITIES)
from .defects import DEFECTS, NEEDS_IMPORTED_1901

GENERATOR_VERSION = "1.3.0"  # 1.3.0: six-digit ingredient HS codes, supplier declarations instead of certificates, no watermark line, table layout for packaging and production notes
# 1.2.0: realistic document layout (letterheads, TIN, unit prices, cost breakdown, equipment)
# 1.1.0  # 1.1.0: four products across subheadings 1901.10 / 1901.20 / 1901.90
RULES_PATH = pathlib.Path(__file__).resolve().parent.parent / "rules" / "rules.json"
STEP_CODES = {
    "Mashing": "mashing_enzymatic", "Filtration and vacuum": "evaporation_concentration", "Filling": "simple_packaging",
    "Labelling": "labelling", "Simple mixing": "simple_mixing", "Cleaning": "cleaning_washing",
    "Roasting": "roasting_toasting", "Cooking by extrusion": "cooking_extrusion", "Drum drying": "drying_drum_spray",
    "Simple grinding": "simple_grinding", "Simple sifting": "simple_sifting_sorting", "Product is processed": "unspecified_processing",
}
C2 = Decimal("0.01")


def tolerance_percent():
    """Threshold read from rules.json, never hard-coded."""
    doc = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    return Decimal(doc["parameters"]["tolerance"]["percent"])


def _m(v, cur="GHS", status="stated"):
    return {"amount": None if v is None else str(v), "currency": cur, "status": status}


def _code(text):
    for k, v in STEP_CODES.items():
        if text.startswith(k):
            return v
    return "unspecified_processing"


def generate_case(spec, seed):
    rng = random.Random(f"{seed}:{spec['case_id']}")
    rec = RECIPES[spec["product"]]
    defects = list(spec.get("defects", []))
    for d in defects:
        assert d in DEFECTS, d
    lang = spec.get("language", "en")
    fmt = spec.get("format", "typed")
    mess = float(spec.get("messiness", 0.3))
    exw = Decimal(spec.get("exw") or rng.choice(["20000", "25000", "40000", "50000", "60000", "80000"]))
    tol = tolerance_percent()

    name = f"{rng.choice(FIRST)} {rng.choice(SECOND)} Ltd"
    town = rng.choice(TOWNS)
    dest = spec.get("destination") or rng.choice(list(CONSIGNEE_CITIES))
    exporter = {"name": name, "address": f"Plot {rng.randint(1, 99)}, Light Industrial Area, {town}, Ghana",
                "registration_no": None if "D13_missing_exporter_registration" in defects else f"GEPA/EXP/2026/{rng.randint(1000, 9999)}",
                "registration_status": "Registered company (Office of the Registrar of Companies)",
                "tin": f"C00{rng.randint(10000000, 99999999)}", "phone": f"+233 {rng.choice(['30', '32', '37', '24', '55'])} {rng.randint(100, 999)} {rng.randint(1000, 9999)}"}
    consignee = {"name": f"{rng.choice(BUYER_FIRST)} {rng.choice(BUYER_SECOND)}",
                 "address": f"{rng.randint(1, 200)} {rng.choice(['Market Road', 'Avenue de la Paix', 'Harbour Road', 'Industrial Layout'])}, {CONSIGNEE_CITIES[dest]}", "country": dest}

    # ---- inputs -------------------------------------------------------------
    inputs = []
    for i, ing in enumerate(rec["ingredients"], 1):
        origin = spec.get("origins", {}).get(ing["key"]) or rng.choice(ing["origins"])
        country = "Ghana" if origin == "ghana" else (rng.choice(STATE_PARTY_SUPPLIERS) if origin == "state_party"
                                                     else rng.choice(NON_STATE_PARTY_SUPPLIERS))
        country = spec.get("countries", {}).get(ing["key"], country)
        cv = (exw * Decimal(str(rng.uniform(*ing["share"])))).quantize(C2, ROUND_HALF_UP)
        fob = cv if origin != "non_state_party" else (cv * Decimal("0.92")).quantize(C2, ROUND_HALF_UP)
        decl = {"ghana": "appendix_iii_a", "state_party": "appendix_iii_a", "non_state_party": "supplier_invoice"}[origin]
        inputs.append({"id": f"I{i}", "description": ing["description"], "hs_code": ing["hs"],
                       "quantity": {"value": ing["qty"], "unit": ing["unit"]},
                       "customs_value": _m(cv), "fob_value": _m(fob), "supplier": _supplier(country, ing["key"], rng),
                       "supplier_country": country, "origin_class": origin, "food_aid": False,
                       "declaration": {"type": decl, "present": True}, "conflicts": [], "_desc_fr": ing.get("desc_fr")})

    # imported heading-19.01 material(s) for tolerance tests
    shares = list(spec.get("split_1901") or ([spec["share_pct"]] if spec.get("share_pct") not in (None, "0") else []))
    if "D07_above_tolerance" in defects and not shares:
        shares = [str(Decimal(rng.randint(160, 250)) / 10)]
    if NEEDS_IMPORTED_1901 & set(defects) and not shares:
        shares = [str(Decimal(rng.randint(20, 100)) / 10)]
    imp = rec["imp1901"]
    for k, pct in enumerate(shares, 1):
        cv = (exw * Decimal(pct) / 100).quantize(C2, ROUND_HALF_UP)
        inputs.append({"id": f"X{k}", "description": imp["description"], "hs_code": imp["hs"],
                       "quantity": {"value": str(rng.randint(20, 120)), "unit": "kg"},
                       "customs_value": _m(cv), "fob_value": _m(cv), "supplier": f"{rng.choice(EU_SUPPLIERS)} {['B.V.', 'GmbH', 'Ltd', 'S.A.'][k % 4]}" + (f" (lot {k})" if len(shares) > 1 else ""),
                       "supplier_country": rng.choice(NON_STATE_PARTY_SUPPLIERS), "origin_class": "non_state_party",
                       "food_aid": False, "declaration": {"type": "supplier_invoice", "present": True}, "conflicts": [],
                       "_target_share_pct": pct, "_desc_fr": imp["desc_fr"]})
    if spec.get("sp_1901") or "D01_missing_supplier_declaration" in defects:
        cv = (exw * Decimal(str(rng.randint(30, 90))) / 1000).quantize(C2, ROUND_HALF_UP)
        has_proof = "D01_missing_supplier_declaration" not in defects
        inputs.append({"id": "SP1", "description": imp["description"], "hs_code": imp["hs"],
                       "quantity": {"value": str(rng.randint(20, 80)), "unit": "kg"}, "customs_value": _m(cv), "fob_value": _m(cv),
                       "supplier": "Brasserie des Plateaux SARL", "supplier_country": "Togo", "origin_class": "state_party",
                       "food_aid": False, "declaration": {"type": "appendix_iii_a" if has_proof else None, "present": has_proof},
                       "conflicts": [], "_desc_fr": imp["desc_fr"]})

    # reality-changing defects
    base = [x for x in inputs if x["id"].startswith("I")]
    if "D06_unstated_origin_other" in defects:
        t = rng.choice(base); t.update(origin_class="unknown", supplier_country=None, declaration={"type": None, "present": False})
    if "D09_food_aid_input" in defects:
        rng.choice([b for b in base if b["description"] in ("Millet grain", "Malt, not roasted", "Soya beans")] or base)["food_aid"] = True

    # ---- process ------------------------------------------------------------
    process = "art7_only" if "D08_simple_operations_only" in defects else spec.get("process", "substantive")
    step_src = list(rec["steps"][process])
    if "D11_ambiguous_process" in defects:
        step_src = [AMBIGUOUS_STEP, step_src[-1]]
    steps = [{"id": f"S{i}", "description": en, "description_fr": fr, "operation_code": _code(en), "location_country": "Ghana"}
             for i, (en, fr) in enumerate(step_src, 1)]

    packaging = []
    for i, p in enumerate(rec["packaging"], 1):
        unknown = p["packing_type"] == "retail" and "D10_packaging_unknown_origin" in defects
        packaging.append({"id": f"P{i}", "description": p["description"], "packing_type": p["packing_type"],
                          "origin_class": "unknown" if unknown else "ghana", "country": None if unknown else "Ghana"})

    product_desc = rec.get("hs_doubt_description") if "D12_doubtful_product_hs" in defects else rec["product_description"]
    b = rec["batch"]
    product = {"description": product_desc, "declared_hs": rec["declared_hs"], "quantity": b["quantity"], "unit": b["unit"],
               "gross_weight_kg": b["gross_weight_kg"], "marks": f"{''.join(w[0] for w in name.split()[:2])}/{dest[:3].upper()}/1-{b['quantity']}",
               "packaging_count": f"{int(b['quantity']) // rec.get('per_carton', 12 if spec['product'] == 'malt_extract' else 20)} cartons",
               "transport": rng.choice([f"Road – truck GR {rng.randint(1000, 9999)}-26, from Tema", f"Road – truck AS {rng.randint(1000, 9999)}-25, via Aflao border", "Sea – MV Gulf Trader, from Tema port"]),
               "statistical_measure": f"{b['gross_weight_kg']} kg"}
    inv_value = (exw * Decimal("1.08")).quantize(C2)
    truth = {"case_id": spec["case_id"], "synthetic": True, "exporter": exporter, "consignee": consignee,
             "destination_country": dest, "product": product, "ex_works_price": _m(exw), "inputs": inputs,
             "production_steps": [{k: v for k, v in s.items() if k != "description_fr"} for s in steps],
             "packaging": packaging,
             "invoice": {"number": f"EXP-{rng.randint(1000, 9999)}", "date": "2026-10-15", "value": str(inv_value),
                         "currency": "GHS", "incoterm": rng.choice(["FCA", "EXW", "CPT"])}}
    fr_names = {x["id"]: x.pop("_desc_fr", None) for x in truth["inputs"]}
    for x in truth["inputs"]:
        x.pop("_target_share_pct", None)

    docs = _documents(truth, steps, spec, defects, lang, fmt, mess, rng, fr_names)
    meta = {"case_id": spec["case_id"], "seed": seed, "generator_version": GENERATOR_VERSION, "synthetic": True,
            "label": "SYNTHETIC – fictional SME and fictional suppliers, generated for testing", "spec": spec, "defects": defects,
            "tolerance_percent_used": str(tol), "imported_1901_shares_pct": shares}
    return {"meta": meta, "truth": truth, "documents": docs}


# ---------------------------------------------------------------------------- documents
def _num(v, mess, rng):
    d = Decimal(str(v))
    s = f"{d:,.2f}" if rng.random() < mess else f"{d:.2f}"
    return s


def _cur(mess, rng):
    return rng.choice(["GHS", "GH₵", "Ghc"]) if rng.random() < mess else "GHS"


def _unit(u, mess, rng):
    if u == "kg" and rng.random() < mess:
        return rng.choice(["kgs", "Kg", "kilos"])
    return u


def _supplier(country, key, rng):
    names = SUPPLIER_NAMES.get(country) or SUPPLIER_NAMES["_other"]
    return rng.choice(names).format(item={"malt": "Malt", "glucose": "Sweeteners", "millet": "Grains", "soya": "Agro",
                                          "sugar": "Sugar", "milk": "Dairy", "wheat": "Flour Mills", "baking": "Bakery Supplies", "cassava": "Cassava Farmers"}.get(key, "Agro"))




def _documents(t, steps, spec, defects, lang, fmt, mess, rng, fr_names):
    docs = []
    hand = fmt == "handwritten"
    exp = t["exporter"]
    batch = f"B-{rng.randint(2600, 2699)}-{rng.randint(10, 99)}"
    docs.append({"doc_id": "DOC-EXP", "type": "exporter_profile", "language": "en", "format": "typed", "text": "\n".join([
        "EXPORTER PROFILE", f"Name: {exp['name']}", f"Address: {exp['address']}", f"Phone: {exp['phone']}",
        f"TIN: {exp['tin']}", f"Registration no: {exp['registration_no'] or ''}", f"Status: {exp['registration_status']}",
        "Activity: manufacture of food preparations"])})
    lines = ["BILL OF MATERIALS", f"Exporter: {exp['name']}", f"Product: {t['product']['description']}",
             f"Declared HS: {t['product']['declared_hs']}", f"Batch: {t['product']['quantity']} {t['product']['unit']}",
             f"Batch no: {batch}", f"Prepared by: Production manager, {exp['name']}",
             "Item | Description | Qty | Unit | Value (customs value if imported) | FOB | Currency | Supplier | Country | HS code | Origin"]
    illegible = []
    for x in t["inputs"]:
        hs = "1107.10" if ("D02_wrong_input_hs" in defects and x["id"] == "X1") else x["hs_code"]
        cur = "EUR" if ("D14_currency_mismatch_1901" in defects and x["id"] == "X1") else _cur(mess, rng)
        cv, fob = _num(x["customs_value"]["amount"], mess, rng), _num(x["fob_value"]["amount"], mess, rng)
        if "D05_unreadable_cost_1901" in defects and x["id"] == "X1":
            cv = fob = "[illegible]"; illegible.append(f"{x['id']}.customs_value"); illegible.append(f"{x['id']}.fob_value")
        origin = {"ghana": "Ghana", "state_party": "AfCFTA State Party", "non_state_party": "Imported (non-State Party)",
                  "unknown": "—"}[x["origin_class"]]
        unit = _unit(x["quantity"]["unit"], mess, rng)
        lines.append(" | ".join([x["id"], x["description"], x["quantity"]["value"], unit, cv, fob, cur, x["supplier"],
                                 x["supplier_country"] or "—", hs, origin]))
    lines.append("PACKAGING")
    lines.append("Item | Description | Packing type | Made in")
    for p in t["packaging"]:
        lines.append(" | ".join([p["id"], p["description"], p["packing_type"], p["country"] or "—"]))
    docs.append({"doc_id": "DOC-BOM", "type": "bill_of_materials", "language": "en", "format": "handwritten" if hand else "typed",
                 "text": "\n".join(lines), "illegible_fields": illegible})
    for x in t["inputs"]:
        d = x["declaration"]
        if not d.get("present") and d.get("type") is None and x["origin_class"] != "non_state_party":
            continue
        fr = lang != "en" and x["supplier_country"] in FRANCOPHONE
        qty, unit = x["quantity"]["value"], x["quantity"]["unit"]
        if "D03_inconsistent_units_1901" in defects and x["id"] == "X1":
            qty, unit = str(max(1, int(qty) // 25)), "bags"
        val = x["customs_value"]["amount"]
        if "D04_invoice_value_mismatch" in defects and x["id"] == "X1":
            val = str((Decimal(val) * Decimal("1.35")).quantize(C2))
        cur = "EUR" if ("D14_currency_mismatch_1901" in defects and x["id"] == "X1") else "GHS"
        unit_price = "[illegible]" if val == "[illegible]" else f"{(Decimal(val) / Decimal(x['quantity']['value'])).quantize(C2)}"
        if "D05_unreadable_cost_1901" in defects and x["id"] == "X1":
            val = unit_price = "[illegible]"
        kind = d["type"] or "supplier_invoice"
        inv_no = f"{x['supplier'][:3].upper()}-{rng.randint(10000, 99999)}"
        date = f"2026-{rng.randint(7, 9):02d}-{rng.randint(1, 28):02d}"
        if fr:
            title = {"appendix_iii_a": "DÉCLARATION DU FOURNISSEUR (Appendice III, Partie A)",
                     "supplier_invoice": "FACTURE"}[kind]
            body = [title, f"Fournisseur : {x['supplier']}", f"Pays d'origine : {x['supplier_country']}",
                    f"Facture n° : {inv_no}", f"Date : {date}", f"Client : {t['exporter']['name']}",
                    f"Marchandises : {fr_names.get(x['id']) or x['description']}", f"Quantité : {qty} {'sacs' if unit == 'bags' else unit}",
                    f"Prix unitaire : {unit_price} {cur}", (f"Valeur en douane : {val} {cur}" if x["origin_class"] == "non_state_party" else f"Valeur facturée : {val} {cur}"),
                    ("Je soussigné déclare que les marchandises figurant sur cette facture ont été produites dans le pays d'origine indiqué ci-dessus et satisfont aux règles d'origine régissant le commerce préférentiel entre les États parties de la ZLECAf." if kind != "supplier_invoice" else "")]
        else:
            title = {"appendix_iii_a": "SUPPLIER DECLARATION (Appendix III, Part A)",
                     "supplier_invoice": "COMMERCIAL INVOICE AND CUSTOMS ENTRY"}[kind]
            body = [title, f"Supplier: {x['supplier']}", f"Country of origin: {x['supplier_country']}",
                    f"Invoice no: {inv_no}", f"Date: {date}", f"Buyer: {t['exporter']['name']}", f"Goods: {x['description']}",
                    f"Quantity: {qty} {unit}", f"Unit price: {unit_price} {cur}", (f"Customs value: {val} {cur}" if x["origin_class"] == "non_state_party" else f"Invoice value: {val} {cur}"),
                    (f"I, the undersigned, declare that the goods listed on this invoice were produced in {x['supplier_country']} and satisfy the rules of origin governing preferential trade between the African Continental Free Trade Area State Parties." if kind != "supplier_invoice" else "")]
        docs.append({"doc_id": f"DOC-SUP-{x['id']}", "type": kind, "input_id": x["id"], "language": "fr" if fr else "en",
                     "format": "typed", "text": "\n".join(l for l in body if l)})
    fr_notes = lang == "fr_mixed"
    food = [x for x in t["inputs"] if x.get("food_aid")]
    lines = ["PROCÉDÉ DE PRODUCTION" if fr_notes else "PRODUCTION PROCESS",
             (f"Lot : {batch}" if fr_notes else f"Batch no: {batch}"),
             "N° | Étape | Lieu | Équipement" if fr_notes else "Step | Description | Location | Equipment"]
    for s in steps:
        eq = next((v for k, v in EQUIPMENT.items() if s["description"].startswith(k)), None) or "—"
        lines.append(" | ".join([s['id'][1:], s['description_fr'] if fr_notes else s['description'], f"{'Usine' if fr_notes else 'Factory'}, Ghana", eq]))
    if food:
        lines.append(("Aide alimentaire : " if fr_notes else "Food aid: ") + f"{food[0]['description']} received from a food assistance programme")
    else:
        lines.append("Aide alimentaire : aucun intrant" if fr_notes else "Food aid: none of the inputs was obtained from food aid")
    docs.append({"doc_id": "DOC-PROC", "type": "production_notes", "language": "fr" if fr_notes else "en",
                 "format": "handwritten" if hand else "typed", "text": "\n".join(lines)})
    exw = Decimal(t["ex_works_price"]["amount"])
    mats = sum((Decimal(x["customs_value"]["amount"]) for x in t["inputs"]), Decimal(0))
    rest = exw - mats
    labour, energy, pack = (rest * Decimal("0.30")).quantize(C2), (rest * Decimal("0.15")).quantize(C2), (rest * Decimal("0.10")).quantize(C2)
    over = (rest * Decimal("0.20")).quantize(C2)
    margin = rest - labour - energy - pack - over
    docs.append({"doc_id": "DOC-COST", "type": "costing_sheet", "language": "en", "format": "typed", "text": "\n".join([
        "COSTING SHEET", f"Batch no: {batch}", f"Batch: {t['product']['quantity']} {t['product']['unit']}",
        f"Materials: {mats:,.2f} GHS", f"Packaging: {pack:,.2f} GHS", f"Direct labour: {labour:,.2f} GHS", f"Energy and water: {energy:,.2f} GHS",
        f"Factory overheads: {over:,.2f} GHS", f"Margin: {margin:,.2f} GHS",
        f"Ex-works price per batch: {_num(t['ex_works_price']['amount'], mess, rng)} GHS"])})
    inv, p, c = t["invoice"], t["product"], t["consignee"]
    docs.append({"doc_id": "DOC-INV", "type": "export_invoice", "language": "en", "format": "typed", "text": "\n".join([
        "EXPORT INVOICE", f"Invoice no: {inv['number']}", f"Date: {inv['date']}", f"Exporter: {exp['name']}", f"Exporter TIN: {exp['tin']}",
        f"Consignee: {c['name']}", f"Consignee address: {c['address']}", f"Destination: {c['country']}", f"Goods: {p['description']}",
        f"Quantity: {p['quantity']} {p['unit']}", f"Gross weight: {p['gross_weight_kg']} kg", f"Marks: {p['marks']}",
        f"Packages: {p['packaging_count']}", f"Transport: {p['transport']}", f"Value: {inv['value']} {inv['currency']}",
        f"Incoterm: {inv['incoterm']}", "Payment: 30 days after invoice date"])})
    return docs
