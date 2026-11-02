import copy, sys, pathlib
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine import load_rules

@pytest.fixture(scope="session")
def rb():
    return load_rules()

def money(a, cur="GHS", status="stated"):
    return {"amount": None if a is None else str(a), "currency": cur, "status": status}

def inp(id, desc, hs, origin, country, cv, fob=None, decl=None, **kw):
    d = {"id": id, "description": desc, "hs_code": hs, "origin_class": origin, "supplier_country": country,
         "supplier": f"Synthetic supplier {id}", "quantity": {"value": "100", "unit": "kg"},
         "customs_value": money(cv), "fob_value": money(fob if fob is not None else cv),
         "food_aid": False, "declaration": {"type": decl, "present": decl is not None}, "conflicts": []}
    d.update(kw); return d

def base_case(extra_1901=None, exw="10000", steps=None):
    c = {"case_id": "T", "synthetic": True,
         "exporter": {"name": "Synthetic Malt Ltd", "address": "Tema, Ghana", "registration_no": "SYN-001"},
         "consignee": {"name": "Synthetic Buyer", "address": "Lagos", "country": "Nigeria"},
         "product": {"description": "Malt extract, liquid, 1 kg jars", "declared_hs": "1901.90"},
         "ex_works_price": money(exw),
         "inputs": [inp("I1", "Malt, not roasted", "11.07", "ghana", "Ghana", "3000", decl="appendix_iii_a"),
                    inp("I2", "Glucose syrup", "17.02", "state_party", "Nigeria", "800", decl="certificate_of_origin")],
         "production_steps": steps or [
             {"id": "S1", "description": "Mashing of malt", "operation_code": "mashing_enzymatic", "location_country": "Ghana"},
             {"id": "S2", "description": "Vacuum evaporation", "operation_code": "evaporation_concentration", "location_country": "Ghana"},
             {"id": "S3", "description": "Filling into jars", "operation_code": "simple_packaging", "location_country": "Ghana"}],
         "packaging": [{"id": "P1", "description": "Glass jar", "packing_type": "retail", "origin_class": "ghana", "hs_code": "Chapter 70"}],
         "invoice": {"number": "INV-1", "date": "2026-10-01", "value": "12000", "currency": "GHS", "incoterm": "FCA"}}
    for x in (extra_1901 or []):
        c["inputs"].append(x)
    return copy.deepcopy(c)
