"""Named defect library. Each defect states its expected finding, severity and provision.
The answer key keeps its OWN copy of the expectations (answer_key/expectations.py);
a test checks that both lists use the same ids. The generator never computes outcomes."""

DEFECTS = {
    "D01_missing_supplier_declaration": {
        "desc": "A heading 19.01 input claimed to originate in another State Party has no proof of origin on file.",
        "expected_finding": "Origin of the input cannot be confirmed", "severity": "major", "provision": "Annex 2, Art. 31(1)"},
    "D02_wrong_input_hs": {
        "desc": "A heading 19.01 input is coded as 11.07 (malt) in the bill of materials although it is malt extract.",
        "expected_finding": "HS code contradicts description", "severity": "major", "provision": "Appendix IV, heading 19.01"},
    "D03_inconsistent_units_1901": {
        "desc": "Quantity of the imported 19.01 input given in kg in the BOM and in bags in the supplier document.",
        "expected_finding": "Contradictory quantity", "severity": "major", "provision": "Annex 2, Art. 22"},
    "D04_invoice_value_mismatch": {
        "desc": "Value of the imported 19.01 input in the BOM differs from the supplier invoice.",
        "expected_finding": "Contradictory customs value", "severity": "major", "provision": "Annex 2, Art. 22"},
    "D05_unreadable_cost_1901": {
        "desc": "Customs value and FOB of the imported 19.01 input are smudged / illegible.",
        "expected_finding": "Value missing or unreadable", "severity": "major", "provision": "Annex 2, Art. 1(y)"},
    "D06_unstated_origin_other": {
        "desc": "Origin of a non-19.01 input is not stated.",
        "expected_finding": "Origin evidence incomplete", "severity": "minor", "provision": "Annex 2, Art. 22"},
    "D07_above_tolerance": {
        "desc": "Imported 19.01 content set above 15% of the ex-works price.",
        "expected_finding": "Exceeds the 15% tolerance", "severity": "critical", "provision": "EX.CL annex item 3 / Appendix IV 19.01"},
    "D08_simple_operations_only": {
        "desc": "Production limited to Article 7(1) operations (cleaning, simple grinding/mixing, packing).",
        "expected_finding": "Processing limited to Article 7 operations", "severity": "critical", "provision": "Annex 2, Art. 7(1)"},
    "D09_food_aid_input": {
        "desc": "One agricultural input was obtained from food aid.",
        "expected_finding": "Input comes from food aid", "severity": "critical", "provision": "Annex 2, Art. 7(2)"},
    "D10_packaging_unknown_origin": {
        "desc": "Origin of the retail packing is not stated.",
        "expected_finding": "Origin of retail packing unknown", "severity": "minor", "provision": "Annex 2, Art. 11(3)"},
    "D11_ambiguous_process": {
        "desc": "Production described only as 'processed at the factory'.",
        "expected_finding": "Process step unclear", "severity": "major", "provision": "Annex 2, Art. 7(3)"},
    "D12_doubtful_product_hs": {
        "desc": "Product description reads like plain millet flour, not a 19.01 preparation (porridge mix only).",
        "expected_finding": "Doubt whether the product belongs to heading 19.01", "severity": "major", "provision": "Appendix IV, heading 19.01"},
    "D13_missing_exporter_registration": {
        "desc": "Exporter registration number missing.",
        "expected_finding": "Exporter registration number missing", "severity": "minor", "provision": "Appendix I, Box 1"},
    "D14_currency_mismatch_1901": {
        "desc": "Value of the imported 19.01 input stated in EUR while the ex-works price is in GHS.",
        "expected_finding": "Currency mismatch", "severity": "major", "provision": "Annex 2, Art. 1(y)"},
}

NEEDS_IMPORTED_1901 = {"D02_wrong_input_hs", "D03_inconsistent_units_1901", "D04_invoice_value_mismatch",
                       "D05_unreadable_cost_1901", "D14_currency_mismatch_1901"}
