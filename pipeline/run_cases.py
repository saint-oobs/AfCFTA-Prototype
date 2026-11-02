"""Runs the full prototype pipeline on every stored case and compares with the answer key.

stage 1 inputs (documents) -> stage 2/3 adapter (stub or recorded live run) -> stage 4 engine ->
citation guard -> comparison with the answer key (read from file).

python -m pipeline.run_cases            writes web/public/data/ and docs/generated/
"""
import json
import pathlib
from collections import Counter
from decimal import Decimal

from adapter import stub
from engine import load_rules, assess, check_citations, ENGINE_VERSION

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "web" / "public" / "data"
CHECK_FIELDS = ("customs_value", "fob_value", "quantity", "unit", "hs_code", "origin_class", "supplier_country")


def _truth_val(x, f):
    if f in ("customs_value", "fob_value"):
        return x[f]["amount"]
    if f == "quantity":
        return x["quantity"]["value"]
    if f == "unit":
        return x["quantity"]["unit"]
    return x.get(f)


def transcription_metrics(case, extracted):
    """Field-level comparison of extracted values with the clean ground truth."""
    illegible = {f for d in case["documents"] for f in d.get("illegible_fields", [])}
    # fields deliberately written wrongly in the documents (document-level defects) are compared with
    # the document, not with reality: the transcription is right if it reproduces the document.
    doc_level = {"D02_wrong_input_hs": {"X1.hs_code": "11.07"}}
    as_written = {}
    for dfc in case["meta"]["defects"]:
        as_written.update(doc_level.get(dfc, {}))
    ex = {i["id"]: i for i in extracted["inputs"]}
    n = correct = flagged = wrong = 0
    errors = []
    for x in case["truth"]["inputs"]:
        e = ex.get(x["id"])
        for f in CHECK_FIELDS:
            n += 1
            tv = as_written.get(f"{x['id']}.{f}", _truth_val(x, f))
            if e is None:
                wrong += 1; errors.append(f"{x['id']}.{f}: input not extracted"); continue
            ev = _truth_val(e, f)
            status = (e.get(f) or {}).get("status") if f in ("customs_value", "fob_value") else None
            if f"{x['id']}.{f}" in illegible:
                if status in ("unreadable", "missing") and ev is None:
                    flagged += 1
                elif ev is not None and tv is not None and Decimal(str(ev)) == Decimal(str(tv)):
                    correct += 1  # recovered from another document
                else:
                    wrong += 1; errors.append(f"{x['id']}.{f}: illegible but value '{ev}' returned")
                continue
            if f in ("customs_value", "fob_value") and ev is not None and tv is not None:
                ok = Decimal(str(ev)) == Decimal(str(tv))
            else:
                ok = (ev == tv) or (f == "origin_class" and tv == "unknown" and ev == "unknown")
            if ok:
                correct += 1
            else:
                wrong += 1; errors.append(f"{x['id']}.{f}: expected '{tv}', got '{ev}'")
    return {"fields": n, "correct": correct, "flagged_unreadable": flagged, "wrong": wrong, "errors": errors}


def compare(result, exp):
    got = result["outcome"]
    ok_outcome = got["label"] == exp["outcome"] and sorted(got["sub_reasons"]) == sorted(exp.get("sub_reasons", []))
    detected, missed = [], []
    for ef in exp.get("expected_findings", []):
        hit = any(f["category"] == ef["category"] and f["severity"] == ef["severity"] for f in result["findings"])
        (detected if hit else missed).append(ef["defect"])
    explained = {(ef["category"], ef["severity"]) for ef in exp.get("expected_findings", [])}
    false_alarms = [f["title"] for f in result["findings"] if f["severity"] in ("critical", "major")
                    and (f["category"], f["severity"]) not in explained]
    return {"outcome_correct": ok_outcome, "expected_outcome": exp["outcome"], "expected_sub_reasons": exp.get("sub_reasons", []),
            "detected": detected, "missed": missed, "false_alarms": false_alarms}


def run_one(case, rb, exp):
    tx = stub.transcribe(case["documents"])
    extracted = tx["case"]
    extracted["case_id"] = case["meta"]["case_id"]
    result = assess(extracted, rb)
    explanation = stub.explain(result)
    cit = check_citations(explanation, rb)
    return {"case_id": case["meta"]["case_id"], "meta": case["meta"], "documents": case["documents"],
            "adapter": {k: v for k, v in tx.items() if k != "case"}, "extracted": extracted, "result": result,
            "explanation": {"text": explanation, "label": stub.LABEL, "citation_check": cit},
            "expected": exp, "comparison": compare(result, exp) if exp else None,
            "transcription": transcription_metrics(case, extracted)}


def main():
    rb = load_rules()
    fixed_key = {c["case_id"]: c for c in json.loads((ROOT / "answer_key" / "fixed_key.json").read_text(encoding="utf-8"))["cases"]}
    eval_key = {c["case_id"]: c for c in json.loads((ROOT / "answer_key" / "eval_key.json").read_text(encoding="utf-8"))["cases"]}
    import shutil
    shutil.rmtree(OUT / "cases", ignore_errors=True)
    (OUT / "cases").mkdir(parents=True, exist_ok=True)
    index, summary = [], Counter()
    for sub, key in (("fixed", fixed_key), ("eval", eval_key)):
        for f in sorted((ROOT / "cases" / sub).glob("*.json")):
            case = json.loads(f.read_text(encoding="utf-8"))
            exp = key.get(case["meta"]["case_id"])
            if sub == "fixed" and exp:
                exp = dict(exp, expected_findings=[{"defect": d, "category": c, "severity": s} for d, c, s in _fixed_findings(case)])
            rec = run_one(case, rb, exp)
            rec["set"] = sub
            (OUT / "cases" / f"{rec['case_id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            cmp = rec["comparison"]
            index.append({"case_id": rec["case_id"], "set": sub, "product": case["meta"]["spec"]["product"],
                          "scenario": case["meta"]["spec"].get("scenario"), "test": case["meta"]["spec"].get("test"),
                          "case_type": case["meta"]["spec"].get("case_type"), "defects": case["meta"]["defects"],
                          "outcome": rec["result"]["outcome"], "expected": cmp["expected_outcome"] if cmp else None,
                          "correct": cmp["outcome_correct"] if cmp else None,
                          "language": case["meta"]["spec"].get("language", "en"), "format": case["meta"]["spec"].get("format", "typed")})
            summary[(sub, cmp["outcome_correct"])] += 1
    (OUT / "index.json").write_text(json.dumps({"engine_version": ENGINE_VERSION, "rulebase_version": rb["rulebase_version"],
                                                "adapter": stub.LABEL, "cases": index}, ensure_ascii=False, indent=1), encoding="utf-8")
    rules_public = {k: v for k, v in rb.items() if k != "_index"}
    (OUT / "rules.json").write_text(json.dumps(rules_public, ensure_ascii=False, indent=1), encoding="utf-8")
    for s in ("fixed", "eval"):
        print(f"{s}: {summary[(s, True)]} correct, {summary[(s, False)]} incorrect")
    return index


def _fixed_findings(case):
    from_defects = {"D08_simple_operations_only": ("article7", "critical"), "D05_unreadable_cost_1901": ("value", "major")}
    out = [(d,) + from_defects[d] for d in case["meta"]["defects"] if d in from_defects]
    shares = case["meta"].get("imported_1901_shares_pct") or []
    if sum(Decimal(s) for s in shares) > Decimal(case["meta"]["tolerance_percent_used"]):
        out.append(("(share above 15% by design)", "rule_1901", "critical"))
    return out


if __name__ == "__main__":
    main()
