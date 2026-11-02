"""CLI: python rules/validate.py  -> exit 1 if rules.json is invalid."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine.rulebase import validate_rules, DEFAULT_PATH
errs = validate_rules(json.loads(DEFAULT_PATH.read_text(encoding="utf-8")))
print("\n".join(errs) if errs else "rules.json valid")
sys.exit(1 if errs else 0)
