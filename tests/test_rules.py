import copy, json
from engine.rulebase import validate_rules, DEFAULT_PATH, load_rules

DOC = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))

def test_rules_json_is_valid():
    assert validate_rules(DOC) == []

def test_fails_if_any_entry_lacks_a_source():
    for field in ("source_file", "page", "provision"):
        bad = copy.deepcopy(DOC)
        bad["rules"][0][field] = ""
        assert any(field in e for e in validate_rules(bad)), field
    bad = copy.deepcopy(DOC); del bad["rules"][3]["source_file"]
    assert validate_rules(bad)

def test_fails_on_unknown_source_file():
    bad = copy.deepcopy(DOC); bad["rules"][0]["source_file"] = "wikipedia.pdf"
    assert validate_rules(bad)

def test_1901_rule_is_verbatim_including_typo():
    r = load_rules()["_index"]["APPIV-1901"]
    assert r["text"].endswith("Manufacture from Materials of any Heading other that of the Product")
    assert r["page"] == "29"

def test_tolerance_is_draft_and_applied():
    rb = load_rules(); r = rb["_index"]["EXCL-AN-3"]
    assert r["legal_status"].startswith("Draft decision text")
    assert r["applied"] is True and rb["parameters"]["tolerance"]["percent"] == "15"

def test_ex_chapter_19_not_applied():
    r = load_rules()["_index"]["APPIV-EXCH19"]
    assert r["applied"] is False and r["legal_status"] == "not applied – group decision"

def test_state_parties_are_34_named_in_para_7():
    sp = load_rules()["state_parties"]["countries"]
    assert len(sp) == 34 and "Ghana" in sp and "Benin" not in sp
