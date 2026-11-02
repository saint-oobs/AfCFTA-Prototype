"""Reproduces the five required tests (Appendix A) and the evaluation set with pytest."""
import json, pathlib
import pytest
from engine import load_rules
from pipeline.run_cases import run_one

ROOT = pathlib.Path(__file__).resolve().parent.parent
RB = load_rules()
FIXED_KEY = {c["case_id"]: c for c in json.loads((ROOT / "answer_key/fixed_key.json").read_text(encoding="utf-8"))["cases"]}
EVAL_KEY = {c["case_id"]: c for c in json.loads((ROOT / "answer_key/eval_key.json").read_text(encoding="utf-8"))["cases"]}

def _case(sub, cid):
    return json.loads((ROOT / "cases" / sub / f"{cid}.json").read_text(encoding="utf-8"))

@pytest.mark.parametrize("cid", sorted(FIXED_KEY))
def test_fixed_case_matches_hand_derived_key(cid):
    exp = FIXED_KEY[cid]
    rec = run_one(_case("fixed", cid), RB, None)
    r = rec["result"]
    assert r["outcome"]["label"] == exp["outcome"]
    assert r["outcome"]["sub_reasons"] == exp["sub_reasons"]
    assert r["components"]["tolerance"]["status"] == exp["rule_1901"]
    if exp["share_percent"] is not None:
        assert float(r["components"]["tolerance"]["share_display"]) == float(exp["share_percent"])
    assert r["components"]["article7"]["status"] == exp["article7"]
    b12 = [b for b in r["folder"]["boxes"] if b["box"] == 12][0]["value"]
    assert b12 == exp["box12"]

def test_t5a_transcription_has_no_errors():
    assert run_one(_case("fixed", "T5a"), RB, None)["transcription"]["wrong"] == 0

def test_t5b_flags_illegible_value_instead_of_guessing():
    t = run_one(_case("fixed", "T5b"), RB, None)["transcription"]
    assert t["flagged_unreadable"] >= 1 and t["wrong"] == 0

def test_revision_R1_two_lots_same_description():
    # Before adapter 1.1.0, T3d returned 'Further information required (contradictory)'.
    assert run_one(_case("fixed", "T3d"), RB, None)["result"]["outcome"]["label"] == "Likely not to qualify"

def test_evaluation_set_against_answer_key():
    correct = 0
    for cid, exp in EVAL_KEY.items():
        rec = run_one(_case("eval", cid), RB, exp)
        correct += rec["comparison"]["outcome_correct"]
    assert len(EVAL_KEY) >= 10
    assert correct == len(EVAL_KEY)
