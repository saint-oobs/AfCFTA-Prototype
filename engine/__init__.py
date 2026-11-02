"""Deterministic AfCFTA rules-of-origin engine for HS heading 19.01 (prototype).
Pure Python standard library. Exact Decimal arithmetic. No language model."""
from .rulebase import load_rules, validate_rules, RulebaseError  # noqa: F401
from .assess import assess, ENGINE_VERSION  # noqa: F401
from .citations import check_citations  # noqa: F401
