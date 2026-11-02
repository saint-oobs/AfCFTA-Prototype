"""Draft compliance folder based on the Appendix I box notes (Boxes 1–15)."""

LABEL = "Draft compliance folder – based on the Appendix I box notes; the official form is not in the attached sources."


def build_folder(case, result, rb, cumulation_countries):
    p = case.get("product") or {}
    exp = case.get("exporter") or {}
    cons = case.get("consignee") or {}
    inv = case.get("invoice") or {}
    outcome = result["outcome"]["label"]
    if outcome == "Likely to qualify":
        if cumulation_countries:
            box12 = {"value": "SC", "detail": "State Parties with which cumulation was used: " + ", ".join(cumulation_countries)}
        else:
            box12 = {"value": "SX", "detail": "Substantial transformation — Change of Tariff Heading (Article 6.1(c))"}
        box12["indicative"] = True
        box12["note"] = "INDICATIVE SUGGESTION ONLY – to be confirmed by the adviser and the Designated Competent Authority."
    else:
        box12 = {"value": None, "indicative": True, "note": "No origin criteria code proposed while the result is '" + outcome + "'."}

    def box(n, value, filled_by="tool"):
        return {"box": n, "rule_id": f"APPI-BOX-{n}", "value": value, "filled_by": filled_by}

    boxes = [
        box(1, {"name": exp.get("name"), "address": exp.get("address"), "registration_no": exp.get("registration_no")}),
        box(2, {"name": cons.get("name"), "address": cons.get("address"), "country": cons.get("country") or case.get("destination_country")}),
        box(3, "Completed by the issuing authority" + (" (a 'CUMULATION' endorsement may apply, Annex 2 Art. 31(3))" if cumulation_countries else ""), "authority"),
        box(4, p.get("transport")),
        box(5, {"marks": p.get("marks"), "quantity": p.get("quantity"), "unit": p.get("unit")}),
        box(6, {"invoice_no": inv.get("number"), "date": inv.get("date"), "value": inv.get("value"),
                "currency": inv.get("currency"), "incoterm": inv.get("incoterm")}),
        box(7, p.get("packaging_count")),
        box(8, p.get("description")),
        box(9, p.get("gross_weight_kg")),
        box(10, p.get("statistical_measure")),
        box(11, p.get("declared_hs")),
        dict(box(12, box12["value"]), **{k: v for k, v in box12.items() if k != "value"}),
        box(13, "To be completed and signed by the exporter (not signed by the tool)", "exporter"),
        box(14, "Completed by the Designated Competent Authority", "authority"),
        box(15, "Completed by the Customs officer at the port of clearance or exit", "customs"),
    ]
    for b in boxes:
        b["missing"] = b["filled_by"] == "tool" and b["box"] != 12 and (b["value"] in (None, "", {}) or (isinstance(b["value"], dict) and not any(b["value"].values())))
    readiness = []
    for b in boxes:
        if b["missing"]:
            readiness.append({"item": f"Box {b['box']} information", "status": "missing", "rule_id": b["rule_id"]})
    for f in result["findings"]:
        if f["severity"] in ("critical", "major"):
            readiness.append({"item": f["title"], "status": "open (" + f["severity"] + ")", "rule_id": f["rule_ids"][0]})
    readiness.append({"item": "Keep supporting documents (production, costs, origin of all materials, shipment)", "status": "check",
                      "rule_id": "A2-22"})
    return {"label": LABEL, "boxes": boxes, "readiness": readiness}
