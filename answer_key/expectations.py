"""The answer key's own expectation table per defect (kept separate from generator/defects.py).
category = the finding category the result should contain (used only to match findings)."""
EXPECT = {
 "D01_missing_supplier_declaration": {"severity": "major", "category": "origin_proof", "effect": "missing", "rule": "A2-31-1"},
 "D02_wrong_input_hs":               {"severity": "major", "category": "hs",           "effect": "contradictory", "rule": "APPIV-1901"},
 "D03_inconsistent_units_1901":      {"severity": "major", "category": "consistency",  "effect": "contradictory", "rule": "A2-22"},
 "D04_invoice_value_mismatch":       {"severity": "major", "category": "consistency",  "effect": "contradictory", "rule": "A2-22"},
 "D05_unreadable_cost_1901":         {"severity": "major", "category": "value",        "effect": "missing", "rule": "A2-1-y"},
 "D06_unstated_origin_other":        {"severity": "minor", "category": "origin_proof", "effect": None, "rule": "A2-22"},
 "D07_above_tolerance":              {"severity": "critical", "category": "rule_1901", "effect": "fail", "rule": "EXCL-AN-3"},
 "D08_simple_operations_only":       {"severity": "critical", "category": "article7",  "effect": "fail", "rule": "A2-7-1"},
 "D09_food_aid_input":               {"severity": "critical", "category": "food_aid",  "effect": "fail", "rule": "A2-7-2"},
 "D10_packaging_unknown_origin":     {"severity": "minor", "category": "packaging",    "effect": None, "rule": "A2-11-3"},
 "D11_ambiguous_process":            {"severity": "major", "category": "process",      "effect": "missing", "rule": "A2-7-3"},
 "D12_doubtful_product_hs":          {"severity": "major", "category": "hs",           "effect": "out_of_rule_base", "rule": "APPIV-1901"},
 "D13_missing_exporter_registration":{"severity": "minor", "category": "form",         "effect": None, "rule": "APPI-BOX-1"},
 "D14_currency_mismatch_1901":       {"severity": "major", "category": "value",        "effect": "contradictory", "rule": "A2-1-y"},
}
ON_X1 = {"D02_wrong_input_hs", "D03_inconsistent_units_1901", "D04_invoice_value_mismatch",
         "D05_unreadable_cost_1901", "D14_currency_mismatch_1901"}
