from decimal import Decimal
from engine import assess, check_citations
from conftest import base_case, inp, money

def imp1901(id, v, **kw):
    return inp(id, "Imported malt extract (19.01)", "1901.90", "non_state_party", "Netherlands", v, **kw)

def run(rb, case, **kw):
    return assess(case, rb, **kw)

def test_zero_share_rule_met_likely(rb):
    r = run(rb, base_case())
    assert r["components"]["rule_1901"]["status"] == "met"
    assert r["components"]["article7"]["status"] == "met"
    assert r["outcome"]["label"] == "Likely to qualify"
    assert [b for b in r["folder"]["boxes"] if b["box"] == 12][0]["value"] == "SX"

def test_boundary_149_150_151(rb):
    out = {}
    for v in ("1490", "1500", "1510"):
        out[v] = run(rb, base_case([imp1901("X", v)]))
    assert out["1490"]["components"]["tolerance"]["status"] == "met via 15% tolerance"
    assert out["1490"]["components"]["tolerance"]["margin_pp_display"] == "0.100"
    assert out["1500"]["components"]["tolerance"]["status"] == "met via 15% tolerance"
    assert out["1500"]["outcome"]["label"] == "Likely to qualify"
    assert out["1510"]["components"]["tolerance"]["status"] == "not met"
    assert out["1510"]["outcome"]["label"] == "Likely not to qualify"
    assert out["1510"]["findings"][0]["severity"] == "critical"

def test_combined_inputs_each_under_but_together_over(rb):
    r = run(rb, base_case([imp1901("X1", "800"), imp1901("X2", "800")]))
    t = r["components"]["tolerance"]
    assert t["total"] == "1600" and t["status"] == "not met"
    assert r["outcome"]["label"] == "Likely not to qualify"

def test_exact_decimal_not_float(rb):
    # 4.65 / 31 == 0.15 exactly, but binary floats give 0.15000000000000002 > 0.15
    assert 4.65 / 31 > 0.15
    r = run(rb, base_case([imp1901("X", "4.65")], exw="31"))
    assert r["components"]["tolerance"]["status"] == "met via 15% tolerance"

def test_article7_only_fails_even_with_zero_1901(rb):
    steps = [{"id": "S1", "description": "Mix flours", "operation_code": "simple_mixing", "location_country": "Ghana"},
             {"id": "S2", "description": "Pack in bags", "operation_code": "simple_packaging", "location_country": "Ghana"}]
    r = run(rb, base_case(steps=steps))
    assert r["components"]["rule_1901"]["status"] == "met"
    assert r["components"]["article7"]["status"] == "not met"
    assert r["outcome"]["label"] == "Likely not to qualify"
    crit = r["findings"][0]
    assert "A2-7-1-o" in crit["rule_ids"] and "A2-7-1-m" in crit["rule_ids"]

def test_article7_applies_when_tolerance_used(rb):
    steps = [{"id": "S1", "description": "Mix", "operation_code": "simple_mixing", "location_country": "Ghana"}]
    r = run(rb, base_case([imp1901("X", "1000")], steps=steps))
    assert r["components"]["tolerance"]["status"] == "met via 15% tolerance"
    assert r["outcome"]["label"] == "Likely not to qualify"

def test_unclear_step_routes_to_fir(rb):
    steps = [{"id": "S1", "description": "processed", "operation_code": "unspecified_processing", "location_country": "Ghana"}]
    r = run(rb, base_case(steps=steps))
    assert r["outcome"] == {"label": "Further information required", "sub_reasons": ["missing"]}

def test_missing_value_never_zero(rb):
    r = run(rb, base_case([imp1901("X", None)]))
    assert r["outcome"]["label"] == "Further information required"
    assert "missing" in r["outcome"]["sub_reasons"]
    assert r["components"]["tolerance"]["status"] == "unclear"

def test_unreadable_value(rb):
    x = imp1901("X", "1000"); x["customs_value"]["status"] = "unreadable"; x["fob_value"]["status"] = "unreadable"
    r = run(rb, base_case([x]))
    assert r["outcome"]["label"] == "Further information required"

def test_determinate_failure_overrides_missing(rb):
    r = run(rb, base_case([imp1901("X1", "2000"), imp1901("X2", None)]))
    assert r["outcome"]["label"] == "Likely not to qualify"
    assert any(f["sub_reason"] == "missing" for f in r["findings"])

def test_missing_hs_on_nonoriginating_input(rb):
    r = run(rb, base_case([inp("X", "Cereal premix", None, "non_state_party", "Brazil", "500")]))
    assert r["outcome"]["label"] == "Further information required"

def test_originating_input_with_unknown_hs_is_fine(rb):
    r = run(rb, base_case([inp("X", "Local premix", None, "ghana", "Ghana", "500", decl="appendix_iii_a")]))
    assert r["outcome"]["label"] == "Likely to qualify"

def test_state_party_1901_without_proof_then_with_proof(rb):
    x = inp("X", "Malt extract from Togo", "1901.90", "state_party", "Togo", "3000")
    r = run(rb, base_case([x]))
    assert r["outcome"]["label"] == "Further information required"
    assert any("A2-31-1" in f["rule_ids"] for f in r["findings"])
    x2 = inp("X", "Malt extract from Togo", "1901.90", "state_party", "Togo", "3000", decl="certificate_of_origin")
    r2 = run(rb, base_case([x2]))
    assert r2["outcome"]["label"] == "Likely to qualify"
    b12 = [b for b in r2["folder"]["boxes"] if b["box"] == 12][0]
    assert b12["value"] == "SC" and b12["indicative"] is True

def test_state_party_not_in_list(rb):
    x = inp("X", "Malt extract", "1901.90", "state_party", "Benin", "3000", decl="certificate_of_origin")
    assert run(rb, base_case([x]))["outcome"]["label"] == "Further information required"

def test_out_of_rule_base_and_doubt(rb):
    c = base_case(); c["product"]["declared_hs"] = "1904.10"
    r = run(rb, c)
    assert r["outcome"] == {"label": "Further information required", "sub_reasons": ["out_of_rule_base"]}
    c = base_case(); c["product"]["hs_doubt"] = True; c["product"]["hs_doubt_reason"] = "plain millet flour only"
    assert run(rb, c)["outcome"]["sub_reasons"] == ["out_of_rule_base"]

def test_food_aid(rb):
    c = base_case(); c["inputs"][0]["food_aid"] = True
    r = run(rb, c)
    assert r["outcome"]["label"] == "Likely not to qualify" and r["findings"][0]["rule_ids"] == ["A2-7-2"]

def test_currency_mismatch_contradictory(rb):
    x = imp1901("X", "100"); x["customs_value"]["currency"] = "USD"
    r = run(rb, base_case([x]))
    assert r["outcome"]["sub_reasons"] == ["contradictory"]

def test_conflict_on_1901_input(rb):
    x = imp1901("X", "500", conflicts=[{"field": "quantity", "values": ["50 kg", "50 bags"], "note": "units differ"}])
    assert run(rb, base_case([x]))["outcome"]["sub_reasons"] == ["contradictory"]

def test_conflict_on_other_input_is_minor(rb):
    c = base_case(); c["inputs"][0]["conflicts"] = [{"field": "quantity", "values": ["1 t", "1000 bags"]}]
    r = run(rb, c)
    assert r["outcome"]["label"] == "Likely to qualify"
    assert any(f["severity"] == "minor" and f["category"] == "consistency" for f in r["findings"])

def test_packaging_unknown_origin_is_minor(rb):
    c = base_case(); c["packaging"][0]["origin_class"] = "unknown"
    r = run(rb, c)
    assert r["outcome"]["label"] == "Likely to qualify"
    f = [f for f in r["findings"] if f["category"] == "packaging"][0]
    assert f["severity"] == "minor" and "A2-11-3" in f["rule_ids"]

def test_fob_sensitivity_flag(rb):
    x = imp1901("X", "1400", fob="1600")
    r = run(rb, base_case([x]))
    assert r["components"]["tolerance"]["status"] == "met via 15% tolerance"
    assert r["components"]["tolerance"]["alternative"]["differs"] is True

def test_ex_chapter_19_note(rb):
    c = base_case([inp("W", "Wheat flour", "11.01", "non_state_party", "Canada", "500")])
    r = run(rb, c)
    assert r["outcome"]["label"] == "Likely to qualify"
    assert r["notes"] and r["notes"][0]["rule_id"] == "APPIV-EXCH19"

def test_findings_sorted_and_cite_only_rulebase(rb):
    c = base_case([imp1901("X1", "2000"), imp1901("X2", None)])
    c["packaging"][0]["origin_class"] = "unknown"
    r = run(rb, c)
    sev = [f["severity"] for f in r["findings"]]
    order = {"critical": 0, "major": 1, "minor": 2}
    assert sev == sorted(sev, key=order.get)
    for f in r["findings"]:
        assert check_citations(f["rule_ids"], rb)["ok"]
        assert check_citations(f["explanation"], rb)["ok"], f["explanation"]

def test_citation_guard(rb):
    assert check_citations("See Art. 7(1)(m) and Article 31(1), Box 12, heading 19.01", rb)["ok"]
    bad = check_citations("Under Article 99 and Art. 7(5), Box 16, heading 21.06, rule APPIV-2106", rb)
    assert not bad["ok"] and len(bad["rejected"]) == 5
    assert not check_citations(["APPIV-1901", "MADE-UP-1"], rb)["ok"]

def test_folder_never_fills_authority_boxes(rb):
    r = run(rb, base_case())
    for b in r["folder"]["boxes"]:
        if b["box"] in (3, 14, 15):
            assert b["filled_by"] in ("authority", "customs")
    assert "not in the attached sources" in r["folder"]["label"]

def test_missing_info_request(rb):
    r = run(rb, base_case([imp1901("X", None)]))
    assert r["missing_info_request"].startswith("Dear Synthetic Malt Ltd")

def test_revision_R2_food_aid_checked_even_out_of_rule_base(rb):
    c = base_case(); c["product"]["hs_doubt"] = True; c["inputs"][0]["food_aid"] = True
    r = run(rb, c)
    assert r["outcome"]["label"] == "Likely not to qualify"
    assert {f["category"] for f in r["findings"]} >= {"food_aid", "hs"}

def test_unclear_share_is_marked_lower_bound(rb):
    r = run(rb, base_case([imp1901("X", None)]))
    assert r["components"]["tolerance"].get("share_is_lower_bound") is True
