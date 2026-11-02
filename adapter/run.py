"""CLI for the adapter.
  python -m adapter.run --case T5a            stub transcription + engine, printed
  python -m adapter.run --case T5a --live     Gemini free tier (needs GEMINI_API_KEY); writes cases/recorded/
"""
import argparse, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--model", default=None)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT))
    from engine import load_rules, assess, check_citations  # the CLI glues adapter + engine (not the adapter module itself)
    from adapter import stub
    rb = load_rules()
    f = next((ROOT / "cases").glob(f"*/{a.case}.json"))
    case = json.loads(f.read_text(encoding="utf-8"))
    if not a.live:
        tx = stub.transcribe(case["documents"]); extracted = tx["case"]; extracted["case_id"] = a.case
        res = assess(extracted, rb)
        print(json.dumps({"label": stub.LABEL, "outcome": res["outcome"], "explanation": stub.explain(res)}, indent=1, ensure_ascii=False))
        return
    from adapter import live
    model = a.model or live.DEFAULT_MODEL
    codes = [m["code"] for m in rb["operation_map"]]
    extracted, meta = live.extract(case["documents"], ROOT / "cases" / "images", a.case, codes, model)
    extracted["case_id"] = a.case
    res = assess(extracted, rb)
    text, emeta = live.explain(res, sorted({r for f_ in res["findings"] for r in f_["rule_ids"]} | {"APPIV-1901", "EXCL-AN-3", "A2-7-1"}), model)
    cit = check_citations(text, rb)
    rec = {"label": "recorded live run", "case_id": a.case, "date": datetime.datetime.now().isoformat(timespec="seconds"),
           "extraction_meta": meta, "explanation_meta": emeta, "extracted": extracted, "result": res,
           "explanation": {"text": text, "citation_check": cit,
                           "status": "accepted" if cit["ok"] else "FLAGGED – cites provisions not in rules.json"}}
    out = ROOT / "cases" / "recorded" / f"{a.case}_{rec['date'].replace(':', '')}.json"
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"recorded live run -> {out}\noutcome: {res['outcome']}\ncitation check: {cit}")


if __name__ == "__main__":
    main()
