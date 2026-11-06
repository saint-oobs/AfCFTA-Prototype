"""Builds the test log data for the website (tests + measured results) and the docs."""
import json, pathlib, shutil
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "public" / "data"
LABELS = ["Likely to qualify", "Likely not to qualify", "Further information required"]
DEFICIENCY_NAMES = {
    "origin_proof": "Proof of origin missing", "value": "Value missing, unreadable or in another currency",
    "consistency": "Contradictory information", "hs": "HS code missing or in doubt", "process": "Production step not clear",
    "food_aid": "Ingredient from food aid", "rule_1901": "Imported 19.01 ingredients above 15%", "article7": "No eligible manufacturing process",
    "packaging": "Origin of packing not stated", "form": "Form data missing",
}


def load(cid):
    return json.loads((DATA / "cases" / f"{cid}.json").read_text(encoding="utf-8"))


def outcome_text(o):
    return o["outcome"] + (f" ({', '.join({'missing': 'information missing', 'contradictory': 'contradictory information', 'out_of_rule_base': 'HS code in doubt'}[s] for s in o['sub_reasons'])})" if o["sub_reasons"] else "")


def main():
    fk = {c["case_id"]: c for c in json.loads((ROOT / "answer_key/fixed_key.json").read_text(encoding="utf-8"))["cases"]}
    groups = [("1", "Typical", ["T1"]), ("2", "Failure", ["T2"]), ("3", "Edge", ["T3a", "T3b", "T3c", "T3d"]),
              ("4", "Edge / difficult", ["T4"]), ("5", "Key assumption", ["T5a", "T5b"])]
    tests = []
    for n, typ, ids in groups:
        first = fk[ids[0]]
        tests.append({"#": n, "case_type": typ, "product": first["product"], "hs": first["declared_hs"],
                      "cases": [{"case_id": c, "scenario": load(c)["meta"]["spec"]["scenario"].split(". ", 1)[-1] if len(ids) > 1 else load(c)["meta"]["spec"]["scenario"].split(". ", 1)[-1],
                                 "expected": outcome_text(fk[c])} for c in ids]})
    fixed = [load(c) for c in fk]
    ev = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((DATA / "cases").glob("E*.json"))]
    tiles = [{"case_id": r["case_id"], "set": "Test cases" if r["case_id"].startswith("T") else "Miscellaneous test logs",
              "result": r["result"]["outcome"]["label"], "sub_reasons": r["result"]["outcome"]["sub_reasons"],
              "agrees": (r["result"]["outcome"]["label"] == fk[r["case_id"]]["outcome"] and r["result"]["outcome"]["sub_reasons"] == fk[r["case_id"]]["sub_reasons"])
              if r["case_id"] in fk else r["comparison"]["outcome_correct"]} for r in fixed + ev]
    found = Counter()
    sev = Counter()
    by_sev = {}
    for r in fixed + ev:
        for f in r["result"]["findings"]:
            name = DEFICIENCY_NAMES.get(f["category"], f["category"])
            found[name] += 1
            sev[f["severity"]] += 1
            by_sev.setdefault(name, Counter())[f["severity"]] += 1
    confusion = {e: {o: 0 for o in LABELS} for e in LABELS}
    for r in ev:
        confusion[r["comparison"]["expected_outcome"]][r["result"]["outcome"]["label"]] += 1
    for c, k in fk.items():
        confusion[k["outcome"]][load(c)["result"]["outcome"]["label"]] += 1
    groups4 = [("typed", False), ("typed", True), ("handwritten", False), ("handwritten", True)]
    tx = {g: Counter() for g in groups4}  # field values per record type
    ncases = Counter()
    for r in fixed + ev:
        sp = r["meta"]["spec"]
        g = ("handwritten" if sp.get("format") == "handwritten" else "typed", sp.get("language", "en") != "en")
        ncases[g] += 1
        for f in ("fields", "correct", "flagged_unreadable", "wrong"):
            tx[g][f] += r["transcription"][f]
    success = {"tiles": tiles, "deficiencies": [{"type": k, "count": v, **{s: by_sev[k][s] for s in ("critical", "major", "minor")}} for k, v in found.most_common()],
               "severity": {s: sev[s] for s in ("critical", "major", "minor")}, "confusion": confusion, "labels": LABELS,
               "transcription": [{"format": g[0], "language": "multilingual" if g[1] else "English", "cases": ncases[g],
                                  **{f: tx[g][f] for f in ("fields", "correct", "flagged_unreadable", "wrong")}} for g in groups4]}
    out = {"tests": tests, "success": success,
           "evaluation_cases": [{"case_id": r["case_id"], "product": r["meta"]["spec"]["product"], "scenario": r["meta"]["spec"].get("scenario"),
                                 "expected": r["comparison"]["expected_outcome"], "observed": r["result"]["outcome"]["label"],
                                 "sub": ", ".join({"missing": "information missing", "contradictory": "contradictory information", "out_of_rule_base": "HS code in doubt"}[x] for x in r["result"]["outcome"]["sub_reasons"])} for r in ev]}
    (DATA / "test_log.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    img = DATA / "images"
    if img.exists():
        shutil.rmtree(img)
    shutil.copytree(ROOT / "cases" / "images", img)
    (DATA / "prompts").mkdir(exist_ok=True)
    for f in (ROOT / "adapter" / "prompts").glob("*.txt"):
        shutil.copy(f, DATA / "prompts" / f.name)
    shutil.copy(ROOT / "adapter" / "stub.py", DATA / "stub_excerpt.txt")
    md = ["# Prototype test log (generated by `python -m pipeline.test_log`)", "", "| # | Case type | Product (HS) | Scenario / input | Expected outcome |", "|---|---|---|---|---|"]
    for t in tests:
        md.append(f"| {t['#']} | {t['case_type']} | {t['product']} ({t['hs']}) | " + "<br>".join(f"{c['case_id']}: {c['scenario']}" for c in t["cases"])
                  + " | " + "<br>".join(f"{c['case_id']}: {c['expected']}" for c in t["cases"]) + " |")
    md += ["", f"Results that agree with the expected assessment under the AfCFTA rules: {sum(t['agrees'] for t in tiles)} of {len(tiles)} cases.",
           f"SME documentation deficiencies reported: {sum(found.values())}."]
    (ROOT / "docs" / "test_log.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"test log: {sum(t['agrees'] for t in tiles)}/{len(tiles)} agree; {sum(found.values())} deficiencies")


if __name__ == "__main__":
    main()
