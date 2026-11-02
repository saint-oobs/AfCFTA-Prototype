"""Loading and validating rules.json (stdlib only, so it also runs in Pyodide)."""
import json
import pathlib

REQUIRED_RULE_FIELDS = ("id", "title", "text", "source_file", "page", "provision",
                        "version_date", "legal_status", "engine_behaviour", "applied")
ALLOWED_SOURCE_FILES = {
    "Agreement_Establishing_the_African_Continental_Free_Trade_Area_1.pdf",
    "EN-APPENDIX-IV-AS-AT-COM-12-DECEMBER-2023_1.pdf",
    "EX_CL_1329_XL_E_1.pdf",
}
DEFAULT_PATH = pathlib.Path(__file__).resolve().parent.parent / "rules" / "rules.json"


class RulebaseError(ValueError):
    pass


def validate_rules(doc):
    """Return a list of error strings (empty list = valid)."""
    errors = []
    if not isinstance(doc, dict):
        return ["rules document must be an object"]
    for key in ("rulebase_version", "product_heading", "parameters", "rules",
                "state_parties", "operation_map", "hs_reference", "decisions", "sources"):
        if key not in doc:
            errors.append(f"missing top-level key: {key}")
    rules = doc.get("rules", [])
    ids = set()
    for i, r in enumerate(rules):
        rid = r.get("id", f"<index {i}>")
        for f in REQUIRED_RULE_FIELDS:
            if f not in r:
                errors.append(f"{rid}: missing field '{f}'")
            elif f != "applied" and (not isinstance(r[f], str) or not r[f].strip()):
                errors.append(f"{rid}: field '{f}' is empty")
        if r.get("source_file") and r["source_file"] not in ALLOWED_SOURCE_FILES:
            errors.append(f"{rid}: source_file not one of the attached sources")
        if r.get("source_file") and r["source_file"] not in doc.get("sources", {}):
            errors.append(f"{rid}: source_file not listed under 'sources'")
        if rid in ids:
            errors.append(f"duplicate id {rid}")
        ids.add(rid)
    tol = doc.get("parameters", {}).get("tolerance", {})
    if tol.get("rule_id") not in ids:
        errors.append("parameters.tolerance.rule_id does not reference a rule")
    for m in doc.get("operation_map", []):
        if m.get("status") not in ("listed", "not_listed", "unclear"):
            errors.append(f"operation {m.get('code')}: bad status")
        if m.get("rule_id") not in ids:
            errors.append(f"operation {m.get('code')}: rule_id not in rules")
    for d in doc.get("decisions", []):
        for rid in d.get("rule_ids", []):
            if rid not in ids:
                errors.append(f"decision {d.get('id')}: unknown rule id {rid}")
    if doc.get("state_parties", {}).get("rule_id") not in ids:
        errors.append("state_parties.rule_id does not reference a rule")
    return errors


def load_rules(path=None, text=None):
    if text is None:
        text = pathlib.Path(path or DEFAULT_PATH).read_text(encoding="utf-8")
    doc = json.loads(text)
    errs = validate_rules(doc)
    if errs:
        raise RulebaseError("; ".join(errs))
    doc["_index"] = {r["id"]: r for r in doc["rules"]}
    return doc
