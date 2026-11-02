"""Small helpers: HS normalisation and exact Decimal parsing."""
import re
from decimal import Decimal, InvalidOperation

USABLE = ("stated", "inferred")


def heading_of(code):
    """'1901.90' / '190190' / '19.01' -> '19.01'. Chapter-level or empty -> None."""
    if not code or not isinstance(code, str):
        return None
    if code.lower().replace("-", " ").strip().startswith(("chapter", "ex chapter", "ex-chapter")):
        return None
    digits = re.sub(r"[^0-9]", "", code)
    if len(digits) < 4:
        return None
    return f"{digits[:2]}.{digits[2:4]}"


def chapter_of(code):
    if not code or not isinstance(code, str):
        return None
    m = re.search(r"chapter\s*(\d{1,2})", code, re.I)
    if m:
        return m.group(1).zfill(2)
    digits = re.sub(r"[^0-9]", "", code)
    return digits[:2] if len(digits) >= 2 else None


def money(field):
    """Return Decimal or None from {'amount': '12.50', 'status': 'stated'}."""
    if not field or not isinstance(field, dict):
        return None
    if field.get("status", "stated") not in USABLE:
        return None
    amt = field.get("amount")
    if amt is None or amt == "":
        return None
    try:
        d = Decimal(str(amt))
    except InvalidOperation:
        return None
    if not d.is_finite() or d < 0:
        return None
    return d


def fmt(d, places="0.01"):
    """Format a Decimal for display only (never used in comparisons)."""
    if d is None:
        return None
    return str(d.quantize(Decimal(places)))
