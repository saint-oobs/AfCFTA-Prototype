"""Derive the expected result of a generated case from its truth + injected defects.
Independent implementation: Fraction arithmetic, own decision table. Reads rules.json only for the threshold."""
import json, pathlib, re
from fractions import Fraction
from .expectations import EXPECT, ON_X1

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "rules" / "rules.json").read_text(encoding="utf-8"))
LIMIT = Fraction(RULES["parameters"]["tolerance"]["percent"])  # 15


def _head(code):
    d = re.sub(r"\D", "", code or "")
    return d[:4] if len(d) >= 4 and not (code or "").lower().startswith(("chapter", "ex")) else None


def derive(case):
    t, defects = case["truth"], case["meta"]["defects"]
    exp = {"case_id": t["case_id"], "defects": defects,
           "expected_findings": [{"defect": d, **EXPECT[d]} for d in defects]}
    if "D12_doubtful_product_hs" in defects:
        # Key revision K1 (2026-11-01): Art. 7(2) applies 'notwithstanding any provision' -> food aid fails the
        # product even when the heading is in doubt. Other findings are not expected (rule not retrieved).
        food = "D09_food_aid_input" in defects
        exp["expected_findings"] = [f for f in exp["expected_findings"] if f["defect"] in ("D12_doubtful_product_hs", "D09_food_aid_input", "D13_missing_exporter_registration", "D10_packaging_unknown_origin")]
        exp.update(outcome="Likely not to qualify" if food else "Further information required",
                   sub_reasons=[] if food else ["out_of_rule_base"], rule_1901="not assessed", share_percent=None, box12=None)
        return exp
    exw = Fraction(t["ex_works_price"]["amount"])
    known, unresolved, cumulation = Fraction(0), False, False
    for x in t["inputs"]:
        if _head(x["hs_code"]) != "1901":
            continue
        if x["origin_class"] == "state_party":
            if x["declaration"]["present"]:
                cumulation = True
            else:
                unresolved = True
            continue
        if x["id"] == "X1" and ON_X1 & set(defects):
            unresolved = True
            continue
        known += Fraction(x["customs_value"]["amount"])
    share = known * 100 / exw
    if share > LIMIT:
        rule = "not met"
    elif unresolved:
        rule = "unclear"
    elif known == 0:
        rule = "met"
    else:
        rule = "met via 15% tolerance"
    critical = rule == "not met" or "D08_simple_operations_only" in defects or "D09_food_aid_input" in defects
    reasons = {EXPECT[d]["effect"] for d in defects if EXPECT[d]["effect"] in ("missing", "contradictory")}
    if critical:
        outcome, subs = "Likely not to qualify", []
    elif reasons:
        outcome, subs = "Further information required", [r for r in ("contradictory", "missing") if r in reasons]
    else:
        outcome, subs = "Likely to qualify", []
    if rule == "not met" and "D07_above_tolerance" not in defects:
        exp["expected_findings"].append({"defect": "(share above 15% by design)", **EXPECT["D07_above_tolerance"]})
    exp.update(outcome=outcome, sub_reasons=subs, rule_1901=rule,
               share_percent=str(round(float(share), 3)) if not unresolved else None,
               box12=("SC" if cumulation else "SX") if outcome == "Likely to qualify" else None)
    return exp


def main():
    out = {"derived_by": "answer_key/derive.py (independent of engine)", "rules_threshold_percent": str(LIMIT), "cases": []}
    for f in sorted((ROOT / "cases" / "eval").glob("*.json")):
        out["cases"].append(derive(json.loads(f.read_text(encoding="utf-8"))))
    (ROOT / "answer_key" / "eval_key.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"answer key for {len(out['cases'])} evaluation cases written")


if __name__ == "__main__":
    main()
