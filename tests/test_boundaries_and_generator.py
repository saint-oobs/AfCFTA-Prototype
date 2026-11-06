import ast, json, pathlib
from generator.core import generate_case, tolerance_percent
from generator.build import FIXED
from generator.defects import DEFECTS
from answer_key.expectations import EXPECT

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = {"engine": {"generator", "answer_key", "adapter"},
             "generator": {"engine", "answer_key", "adapter"},
             "answer_key": {"engine", "generator", "adapter"},
             "adapter": {"engine", "generator", "answer_key"}}

def _imports(pkg):
    names = set()
    for f in (ROOT / pkg).rglob("*.py"):
        if f.name == "run.py" and pkg == "adapter":
            continue  # CLI glue (adapter -> engine), like pipeline/; not adapter logic
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
    return names

def test_modules_do_not_import_each_others_logic():
    for pkg, bad in FORBIDDEN.items():
        assert not (_imports(pkg) & bad), (pkg, _imports(pkg) & bad)

def test_same_seed_same_case_different_seed_differs():
    a = generate_case(FIXED[0], 2026); b = generate_case(FIXED[0], 2026); c = generate_case(FIXED[0], 7)
    assert a == b and a != c

def test_threshold_read_from_rules():
    rules = json.loads((ROOT / "rules" / "rules.json").read_text(encoding="utf-8"))
    assert str(tolerance_percent()) == rules["parameters"]["tolerance"]["percent"]

def test_defect_library_and_answer_key_use_same_ids():
    assert set(DEFECTS) == set(EXPECT)

def test_everything_is_labelled_synthetic():
    for f in (ROOT / "cases").glob("*/*.json"):
        c = json.loads(f.read_text(encoding="utf-8"))
        # v4: the watermark line was removed from the documents at the group's request; the case files stay labelled
        assert c["meta"]["synthetic"] is True and c["truth"]["synthetic"] is True and "SYNTHETIC" in c["meta"]["label"]
        assert not any("certificate of origin" in d["text"].lower() or "certificat d'origine" in d["text"].lower() for d in c["documents"])

def test_state_party_suppliers_only_from_para_7():
    rules = json.loads((ROOT / "rules" / "rules.json").read_text(encoding="utf-8"))
    sp = set(rules["state_parties"]["countries"])
    for f in (ROOT / "cases").glob("*/*.json"):
        for x in json.loads(f.read_text(encoding="utf-8"))["truth"]["inputs"]:
            if x["origin_class"] == "state_party":
                assert x["supplier_country"] in sp
            if x["origin_class"] == "non_state_party":
                assert x["supplier_country"] not in sp
