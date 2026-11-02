"""Evidence discipline: a language-model output may only cite provisions that exist in rules.json.

check_citations(text_or_ids, rb) returns {"ok": bool, "valid": [...], "rejected": [...]}.
- Rule ids (e.g. 'APPIV-1901') must exist in rules.json.
- Free-text references such as 'Article 7(1)(m)', 'Art. 31(1)', 'Box 12', 'heading 19.03'
  must map to a provision present in rules.json.
"""
import re

_ID = re.compile(r"\b(?:A2|APPI|APPIV|EXCL)-[A-Za-z0-9.\-]+\b")
_ART = re.compile(r"\bArt(?:icle|\.)?\s*(\d+)((?:\s*\(\s*[0-9a-z]+\s*\))*)", re.I)
_BOX = re.compile(r"\bBox\s*(\d+)\b", re.I)
_HEAD = re.compile(r"\b(?:heading|HS)\s*(\d{2})\.?(\d{2})\b", re.I)


def _known_provisions(rb):
    known = set()
    for r in rb["rules"]:
        m = re.search(r"Art\.\s*(\d+)((?:\([0-9a-z]+\))*)", r["provision"])
        if r["provision"].startswith("Annex 2") and m:
            parts = re.findall(r"\(([0-9a-z]+)\)", m.group(2))
            # register 'N', 'N(1)', 'N(1)(m)'... and ranges like 6(1)(a)–(d)
            for i in range(len(parts) + 1):
                known.add((m.group(1),) + tuple(parts[:i]))
            rng = re.search(r"\(([a-z])\)–\(([a-z])\)", r["provision"])
            if rng:
                for c in range(ord(rng.group(1)), ord(rng.group(2)) + 1):
                    known.add((m.group(1),) + tuple(parts[:1]) + (chr(c),))
            rng2 = re.search(r"\((\d)\)–\((\d)\)", r["provision"])
            if rng2:
                for c in range(int(rng2.group(1)), int(rng2.group(2)) + 1):
                    known.add((m.group(1), str(c)))
    return known


def check_citations(cited, rb):
    idx = rb["_index"]
    known = _known_provisions(rb)
    boxes = {r["id"].split("-")[-1] for r in rb["rules"] if r["id"].startswith("APPI-BOX-")}
    headings = {"19.01"} | {h["code"] for h in rb.get("hs_reference", []) if h.get("level") == "heading"}
    valid, rejected = [], []
    if isinstance(cited, (list, tuple)):
        for c in cited:
            (valid if c in idx else rejected).append(c)
        return {"ok": not rejected, "valid": valid, "rejected": rejected}
    text = cited or ""
    for m in _ID.finditer(text):
        (valid if m.group(0) in idx else rejected).append(m.group(0))
    for m in _ART.finditer(text):
        parts = tuple(p.strip() for p in re.findall(r"\(\s*([0-9a-z]+)\s*\)", m.group(2)))
        key = (m.group(1),) + parts
        (valid if key in known else rejected).append(m.group(0).strip())
    for m in _BOX.finditer(text):
        (valid if m.group(1) in boxes else rejected).append(m.group(0))
    for m in _HEAD.finditer(text):
        h = f"{m.group(1)}.{m.group(2)}"
        (valid if h in headings else rejected).append(m.group(0))
    return {"ok": not rejected, "valid": valid, "rejected": rejected}
