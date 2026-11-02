"""python -m generator.build [--seed 2026] [--n 44] [--messiness 0.3]
Writes cases/fixed/, cases/eval/, cases/readable/ and cases/manifest.json."""
import argparse, json, pathlib, random
from .core import generate_case, GENERATOR_VERSION
from .defects import DEFECTS

ROOT = pathlib.Path(__file__).resolve().parent.parent / "cases"

FIXED = [
 {"case_id": "T1", "test": 1, "case_type": "Typical", "product": "malt_extract", "share_pct": "0", "exw": "40000",
  "origins": {"malt": "ghana", "glucose": "state_party"}, "countries": {"glucose": "Nigeria"},
  "scenario": "Malt extract (HS 1901.90). Malt from Ghana. Glucose syrup from Nigeria, with a certificate of origin. Mashing and evaporation in Ghana."},
 {"case_id": "T2", "test": 2, "case_type": "Typical", "product": "infant_cereal", "share_pct": "0", "exw": "60000",
  "origins": {"millet": "ghana", "soya": "state_party", "milk": "non_state_party", "sugar": "non_state_party"},
  "countries": {"soya": "Togo"}, "language": "fr_suppliers",
  "scenario": "Infant cereal (HS 1901.10). Imported milk powder and sugar. Soya from Togo, with a French certificate. Roasting, extrusion cooking and drum drying in Ghana."},
 {"case_id": "T3a", "test": 3, "case_type": "Edge", "product": "bread_mix", "share_pct": "14.9", "exw": "40000",
  "origins": {"wheat": "non_state_party", "malt": "ghana", "baking": "ghana", "sugar": "non_state_party"},
  "scenario": "Malted bread mix (HS 1901.20). Imported bakery premix of heading 19.01 = 14.9% of the ex-works price."},
 {"case_id": "T3b", "test": 3, "case_type": "Edge", "product": "bread_mix", "share_pct": "15.0", "exw": "40000",
  "origins": {"wheat": "non_state_party", "malt": "ghana", "baking": "ghana", "sugar": "non_state_party"},
  "scenario": "Malted bread mix (HS 1901.20). Imported bakery premix of heading 19.01 = exactly 15.0%."},
 {"case_id": "T3c", "test": 3, "case_type": "Edge", "product": "bread_mix", "share_pct": "15.1", "exw": "40000",
  "origins": {"wheat": "non_state_party", "malt": "ghana", "baking": "ghana", "sugar": "non_state_party"},
  "scenario": "Malted bread mix (HS 1901.20). Imported bakery premix of heading 19.01 = 15.1%."},
 {"case_id": "T3d", "test": 3, "case_type": "Edge", "product": "bread_mix", "split_1901": ["8.0", "8.0"], "exw": "40000",
  "origins": {"wheat": "non_state_party", "malt": "ghana", "baking": "ghana", "sugar": "non_state_party"},
  "scenario": "Malted bread mix (HS 1901.20). Two imported premix lots of heading 19.01, 8.0% each. Each lot is below 15%, together 16.0%."},
 {"case_id": "T4", "test": 4, "case_type": "Failure", "product": "millet_porridge_mix", "share_pct": "0", "exw": "50000",
  "origins": {"millet": "ghana", "soya": "ghana", "sugar": "non_state_party", "milk": "non_state_party"},
  "defects": ["D08_simple_operations_only"],
  "scenario": "Millet porridge mix (HS 1901.90). Only cleaning, simple grinding, simple mixing and bagging. No imported ingredient of heading 19.01."},
 {"case_id": "T5a", "test": 5, "case_type": "Key assumption", "product": "infant_cereal", "share_pct": "6.0", "exw": "60000",
  "origins": {"millet": "state_party", "soya": "ghana", "milk": "non_state_party", "sugar": "non_state_party"}, "countries": {"millet": "Burkina Faso"},
  "language": "fr_mixed", "format": "handwritten", "messiness": 0.8,
  "scenario": "Infant cereal (HS 1901.10). Handwritten bill of materials, French production notes and a French certificate from Burkina Faso. All values can be read."},
 {"case_id": "T5b", "test": 5, "case_type": "Key assumption", "product": "infant_cereal", "share_pct": "6.0", "exw": "60000",
  "origins": {"millet": "state_party", "soya": "ghana", "milk": "non_state_party", "sugar": "non_state_party"}, "countries": {"millet": "Burkina Faso"},
  "language": "fr_mixed", "format": "handwritten", "messiness": 0.8, "defects": ["D05_unreadable_cost_1901"],
  "scenario": "Same records as T5a, but the value of the imported premix of heading 19.01 is smudged and cannot be read."},
]

INCOMPATIBLE = [({"D07_above_tolerance"}, {"D02_wrong_input_hs", "D03_inconsistent_units_1901", "D04_invoice_value_mismatch",
                                           "D05_unreadable_cost_1901", "D14_currency_mismatch_1901"}),
                ({"D08_simple_operations_only"}, {"D11_ambiguous_process"})]


EVAL = [  # curated evaluation set: SME documentation deficiencies, mainly missing and contradictory information
 ("E01", "malt_extract", ["D01_missing_supplier_declaration"], "en", "typed", "Malt extract with a lot from Togo. The certificate of origin for that lot is missing."),
 ("E02", "bread_mix", ["D05_unreadable_cost_1901"], "en", "handwritten", "Bread mix. The value of the imported premix is smudged."),
 ("E03", "millet_porridge_mix", ["D11_ambiguous_process"], "en", "typed", "Porridge mix. The production notes only say 'processed at the factory'."),
 ("E04", "infant_cereal", ["D03_inconsistent_units_1901"], "fr_suppliers", "typed", "Infant cereal. The premix is in kg in the bill of materials but in bags on the invoice."),
 ("E05", "malt_extract", ["D04_invoice_value_mismatch"], "fr_suppliers", "typed", "Malt extract. The bill of materials and the supplier invoice show different values for the concentrate."),
 ("E06", "bread_mix", ["D14_currency_mismatch_1901"], "en", "typed", "Bread mix. The premix value is in EUR, the ex-works price in GHS."),
 ("E07", "infant_cereal", ["D02_wrong_input_hs"], "en", "typed", "Infant cereal. The premix has the HS code of malt (11.07)."),
 ("E08", "millet_porridge_mix", ["D12_doubtful_product_hs"], "en", "typed", "The product description reads like plain millet flour."),
 ("E09", "infant_cereal", ["D09_food_aid_input"], "fr_mixed", "typed", "Infant cereal. The millet comes from a food assistance programme."),
 ("E10", "malt_extract", ["D07_above_tolerance", "D10_packaging_unknown_origin"], "en", "typed", "Malt extract with imported concentrate above 15%. The origin of the jars is not stated."),
 ("E11", "bread_mix", ["D13_missing_exporter_registration", "D06_unstated_origin_other"], "en", "mixed_units", "Bread mix. No exporter registration number; the origin of one ingredient is not stated."),
 ("E12", "malt_extract", ["D01_missing_supplier_declaration", "D03_inconsistent_units_1901"], "en", "typed", "Malt extract. A certificate is missing and the units of the concentrate do not agree."),
]


def eval_specs(seed, n, messiness):
    return [{"case_id": cid, "product": prod, "share_pct": "0", "defects": ds, "process": "substantive", "language": lang,
             "format": fmt, "messiness": messiness, "scenario": sc} for cid, prod, ds, lang, fmt, sc in EVAL][:n]


def write(case, sub):
    d = ROOT / sub; d.mkdir(parents=True, exist_ok=True)
    (d / f"{case['meta']['case_id']}.json").write_text(json.dumps(case, ensure_ascii=False, indent=1), encoding="utf-8")
    r = ROOT / "readable"; r.mkdir(parents=True, exist_ok=True)
    md = [f"# Case {case['meta']['case_id']} – SYNTHETIC", "", f"Generator {GENERATOR_VERSION}, seed {case['meta']['seed']}",
          f"Defects injected: {', '.join(case['meta']['defects']) or 'none'}", ""]
    for doc in case["documents"]:
        md += [f"## {doc['doc_id']} ({doc['type']}, {doc['language']}, {doc['format']})", "```", doc["text"], "```", ""]
    (r / f"{case['meta']['case_id']}.md").write_text("\n".join(md), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--messiness", type=float, default=0.3)
    a = ap.parse_args(argv)
    manifest = {"generator_version": GENERATOR_VERSION, "seed": a.seed, "messiness": a.messiness, "fixed": [], "eval": [],
                "note": "Synthetic data reflects the team's assumptions about SME records, not observed Ghanaian practice."}
    for spec in FIXED:
        c = generate_case(spec, a.seed); write(c, "fixed"); manifest["fixed"].append(spec["case_id"])
    for spec in eval_specs(a.seed, a.n, a.messiness):
        c = generate_case(spec, a.seed); write(c, "eval"); manifest["eval"].append(spec["case_id"])
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"wrote {len(manifest['fixed'])} fixed and {len(manifest['eval'])} evaluation cases to {ROOT}")


if __name__ == "__main__":
    main()
