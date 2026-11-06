"""Product recipes for synthetic SMEs (heading 19.01 only). All names and firms are fictional.

HS codes for inputs are six-digit HS 2022 subheadings as an SME or supplier would declare them
(revision v4: replaces the earlier heading/chapter-level codes). They are synthetic declarations, not verified classifications;
the engine uses only the first four digits (the heading). Product subheadings
(1901.10 / 1901.20 / 1901.90) are SME-declared and not verified. The 19.01 rule applies to all of them.
"""

STATE_PARTY_SUPPLIERS = ["Nigeria", "Togo", "Côte d’Ivoire", "Burkina Faso", "Senegal", "Mali", "Kenya", "Egypt"]
FRANCOPHONE = {"Togo", "Côte d’Ivoire", "Burkina Faso", "Senegal", "Mali"}
NON_STATE_PARTY_SUPPLIERS = ["Netherlands", "Belgium", "Brazil", "New Zealand", "France", "India"]

# role: 'base' ingredient, 'imp1901' = optional imported heading-19.01 material used for tolerance tests.
RECIPES = {
    "malt_extract": {
        "product_description": "Malt extract, liquid, in 1 kg plastic jars",
        "declared_hs": "1901.90",
        "batch": {"quantity": "1000", "unit": "jars", "gross_weight_kg": "1150"},
        "ingredients": [
            {"key": "malt", "description": "Malt, not roasted", "desc_fr": "Malt, non torréfié", "hs": "1107.10", "qty": "800", "unit": "kg",
             "share": (0.18, 0.26), "origins": ["ghana", "state_party"]},
            {"key": "glucose", "description": "Glucose syrup", "desc_fr": "Sirop de glucose", "hs": "1702.30", "qty": "150", "unit": "kg",
             "share": (0.04, 0.08), "origins": ["state_party", "non_state_party", "ghana"]},
        ],
        "imp1901": {"description": "Malt extract concentrate", "hs": "1901.90", "unit": "kg",
                    "desc_fr": "Extrait de malt concentré"},
        "packaging": [
            {"description": "Plastic jar with lid, 1 kg", "packing_type": "retail"},
            {"description": "Corrugated carton (12 jars)", "packing_type": "transport"},
        ],
        "steps": {
            "substantive": [
                ("Mashing of malt with hot water in a mash tun (enzymatic conversion)", "Brassage du malt à l'eau chaude"),
                ("Filtration and vacuum evaporation to a concentrate", "Filtration et évaporation sous vide"),
                ("Filling into jars", "Remplissage des pots"),
                ("Labelling", "Étiquetage"),
            ],
            "art7_only": [
                ("Simple mixing of purchased malt extract with glucose syrup", "Simple mélange d'extrait de malt acheté et de sirop de glucose"),
                ("Filling into jars", "Remplissage des pots"),
                ("Labelling", "Étiquetage"),
            ],
        },
    },
    "millet_porridge_mix": {
        "product_description": "Instant millet porridge mix (precooked millet and soya flour with sugar and milk powder), 500 g pouches",
        "declared_hs": "1901.90",
        "batch": {"quantity": "2000", "unit": "pouches", "gross_weight_kg": "1080"},
        "ingredients": [
            {"key": "millet", "description": "Millet grain", "desc_fr": "Mil en grains", "hs": "1008.29", "qty": "600", "unit": "kg",
             "share": (0.12, 0.18), "origins": ["ghana", "state_party"]},
            {"key": "soya", "description": "Soya beans", "desc_fr": "Fèves de soja", "hs": "1201.90", "qty": "200", "unit": "kg",
             "share": (0.05, 0.08), "origins": ["ghana", "state_party"]},
            {"key": "sugar", "description": "Cane sugar", "desc_fr": "Sucre de canne", "hs": "1701.99", "qty": "120", "unit": "kg",
             "share": (0.03, 0.05), "origins": ["non_state_party", "state_party"]},
            {"key": "milk", "description": "Skimmed milk powder", "desc_fr": "Lait écrémé en poudre", "hs": "0402.10", "qty": "80", "unit": "kg",
             "share": (0.06, 0.10), "origins": ["non_state_party"]},
        ],
        "imp1901": {"description": "Cereal-based premix preparation", "hs": "1901.90", "unit": "kg",
                    "desc_fr": "Prémélange céréalier préparé"},
        "packaging": [
            {"description": "Printed plastic pouch, 500 g", "packing_type": "retail"},
            {"description": "Corrugated carton (20 pouches)", "packing_type": "transport"},
        ],
        "steps": {
            "substantive": [
                ("Cleaning of millet", "Nettoyage du mil"),
                ("Roasting of millet and soya", "Torréfaction du mil et du soja"),
                ("Cooking by extrusion", "Cuisson par extrusion"),
                ("Drum drying of the cooked paste", "Séchage sur cylindre de la pâte cuite"),
                ("Simple grinding", "Simple broyage"),
                ("Simple mixing with sugar and milk powder", "Simple mélange avec sucre et lait en poudre"),
                ("Filling into pouches", "Mise en sachets"),
            ],
            "art7_only": [
                ("Cleaning of millet", "Nettoyage du mil"),
                ("Simple grinding", "Simple broyage"),
                ("Simple mixing with sugar and milk powder", "Simple mélange avec sucre et lait en poudre"),
                ("Filling into pouches", "Mise en sachets"),
            ],
        },
        "hs_doubt_description": "Millet flour, ground millet only, no other ingredient, 500 g bags",
    },
    "infant_cereal": {
        "product_description": "Infant cereal (precooked millet and soya with milk powder), for infants and young children, 400 g cartons",
        "declared_hs": "1901.10",
        "per_carton": 24,
        "batch": {"quantity": "2400", "unit": "cartons of 400 g", "gross_weight_kg": "1050"},
        "ingredients": [
            {"key": "millet", "description": "Millet grain", "desc_fr": "Mil en grains", "hs": "1008.29", "qty": "550", "unit": "kg",
             "share": (0.12, 0.18), "origins": ["ghana", "state_party"]},
            {"key": "soya", "description": "Soya beans", "desc_fr": "Fèves de soja", "hs": "1201.90", "qty": "250", "unit": "kg",
             "share": (0.05, 0.08), "origins": ["ghana", "state_party"]},
            {"key": "milk", "description": "Skimmed milk powder", "desc_fr": "Lait écrémé en poudre", "hs": "0402.10", "qty": "120", "unit": "kg",
             "share": (0.08, 0.12), "origins": ["non_state_party"]},
            {"key": "sugar", "description": "Cane sugar", "desc_fr": "Sucre de canne", "hs": "1701.99", "qty": "60", "unit": "kg",
             "share": (0.02, 0.04), "origins": ["non_state_party", "state_party"]},
        ],
        "imp1901": {"description": "Cereal-based premix preparation", "hs": "1901.90", "unit": "kg", "desc_fr": "Prémélange céréalier préparé"},
        "packaging": [
            {"description": "Printed paperboard carton with inner bag, 400 g", "packing_type": "retail"},
            {"description": "Corrugated carton (24 cartons)", "packing_type": "transport"},
        ],
        "steps": {
            "substantive": [
                ("Cleaning of millet", "Nettoyage du mil"),
                ("Roasting of millet and soya", "Torréfaction du mil et du soja"),
                ("Cooking by extrusion", "Cuisson par extrusion"),
                ("Drum drying of the cooked paste", "Séchage sur cylindre de la pâte cuite"),
                ("Simple grinding", "Simple broyage"),
                ("Simple mixing with milk powder and sugar", "Simple mélange avec lait en poudre et sucre"),
                ("Filling into cartons", "Remplissage des boîtes"),
            ],
            "art7_only": [
                ("Cleaning of millet", "Nettoyage du mil"),
                ("Simple grinding", "Simple broyage"),
                ("Simple mixing with milk powder and sugar", "Simple mélange avec lait en poudre et sucre"),
                ("Filling into cartons", "Remplissage des boîtes"),
            ],
        },
    },
    "bread_mix": {
        "product_description": "Malted bread mix (wheat flour with dried malt extract and baking powder), for home baking, 1 kg bags",
        "declared_hs": "1901.20",
        "per_carton": 10,
        "batch": {"quantity": "1500", "unit": "bags of 1 kg", "gross_weight_kg": "1560"},
        "ingredients": [
            {"key": "wheat", "description": "Wheat flour", "desc_fr": "Farine de blé", "hs": "1101.00", "qty": "1100", "unit": "kg",
             "share": (0.20, 0.28), "origins": ["non_state_party", "state_party"]},
            {"key": "malt", "description": "Malt, not roasted", "desc_fr": "Malt, non torréfié", "hs": "1107.10", "qty": "250", "unit": "kg",
             "share": (0.06, 0.10), "origins": ["ghana", "state_party"]},
            {"key": "baking", "description": "Baking powder", "desc_fr": "Levure chimique", "hs": "2102.30", "qty": "40", "unit": "kg",
             "share": (0.01, 0.02), "origins": ["non_state_party", "ghana"]},
            {"key": "sugar", "description": "Cane sugar", "desc_fr": "Sucre de canne", "hs": "1701.99", "qty": "80", "unit": "kg",
             "share": (0.02, 0.04), "origins": ["non_state_party", "state_party"]},
        ],
        "imp1901": {"description": "Bakery premix preparation", "hs": "1901.20", "unit": "kg", "desc_fr": "Prémélange de boulangerie préparé"},
        "packaging": [
            {"description": "Printed paper bag, 1 kg", "packing_type": "retail"},
            {"description": "Corrugated carton (10 bags)", "packing_type": "transport"},
        ],
        "steps": {
            "substantive": [
                ("Mashing of malt with hot water in a mash tun (enzymatic conversion)", "Brassage du malt à l'eau chaude"),
                ("Drum drying of the malt extract with part of the flour", "Séchage sur cylindre de l'extrait de malt avec une partie de la farine"),
                ("Simple mixing with flour, sugar and baking powder", "Simple mélange avec farine, sucre et levure chimique"),
                ("Filling into bags", "Mise en sachets"),
            ],
            "art7_only": [
                ("Simple sifting of flour", "Simple tamisage de la farine"),
                ("Simple mixing with flour, sugar and baking powder", "Simple mélange avec farine, sucre et levure chimique"),
                ("Filling into bags", "Mise en sachets"),
            ],
        },
    },
}

RECIPES["cassava_flour"] = {  # v4.2: product for the HS-doubt test (declared 1901.20, description reads like plain flour)
    "product_description": "Cassava flour for baking (dried cassava, ground only, no other ingredient), 1 kg bags",
    "hs_doubt_description": "Cassava flour for baking (dried cassava, ground only, no other ingredient), 1 kg bags",
    "declared_hs": "1901.20",
    "per_carton": 25,
    "batch": {"quantity": "1200", "unit": "bags of 1 kg", "gross_weight_kg": "1240"},
    "ingredients": [
        {"key": "cassava", "description": "Dried cassava chips", "desc_fr": "Cossettes de manioc séchées", "hs": "0714.10", "qty": "1300", "unit": "kg",
         "share": (0.35, 0.45), "origins": ["ghana"]},
    ],
    "imp1901": {"description": "Bakery premix preparation", "hs": "1901.20", "unit": "kg", "desc_fr": "Prémélange de boulangerie préparé"},
    "packaging": [
        {"description": "Printed paper bag, 1 kg", "packing_type": "retail"},
        {"description": "Woven polypropylene sack (25 bags)", "packing_type": "transport"},
    ],
    "steps": {
        "substantive": [
            ("Cleaning of dried cassava chips", "Nettoyage des cossettes de manioc"),
            ("Simple grinding", "Simple broyage"),
            ("Simple sifting of flour", "Simple tamisage de la farine"),
            ("Filling into bags", "Mise en sachets"),
        ],
    },
}

SUBHEADING_TEXT = {  # HS nomenclature text, NOT in the attached sources – shown as a label only
    "1901.10": "Preparations suitable for infants or young children, put up for retail sale",
    "1901.20": "Mixes and doughs for the preparation of bakers' wares of heading 19.05",
    "1901.90": "Other",
}

AMBIGUOUS_STEP = ("Product is processed at the factory", "Le produit est traité à l'usine")

EU_SUPPLIERS = ["Lowlands Malt Ingredients", "Rhinefield Food Ingredients", "Nordhavn Cereal Premix", "Atlantica Bakery Ingredients", "Westbrook Nutrition Ingredients"]
BUYER_FIRST = ["Sahel", "Lagune", "Kilimanjaro", "Niger Delta", "Baobab", "Teranga"]
BUYER_SECOND = ["Distribution SARL", "Foods Ltd", "Trading SA", "Wholesale Ltd"]
SUPPLIER_NAMES = {  # fictional names
    "Ghana": ["Nkwanta {item} Enterprise", "Akatsi {item} Ltd", "Brong {item} Cooperative", "Ejura {item} Traders"],
    "Nigeria": ["Kano {item} Industries Ltd", "Ogun {item} Ltd"], "Togo": ["Plateaux {item} SARL", "Kara {item} SARL"],
    "Côte d’Ivoire": ["Bouaké {item} SA", "Lagunes {item} SARL"], "Burkina Faso": ["Faso {item} SARL", "Houet {item} SARL"],
    "Senegal": ["Thiès {item} SA"], "Mali": ["Ségou {item} SARL"], "Kenya": ["Rift {item} Ltd"], "Egypt": ["Delta {item} Co."],
    "Netherlands": ["Lowlands {item} B.V.", "Zeeland {item} B.V."], "Belgium": ["Flandria {item} NV", "Brabant {item} NV"],
    "Brazil": ["Paraná {item} Ltda", "Minas {item} Ltda"], "New Zealand": ["Southern Cross {item} Ltd", "Waikato {item} Ltd"],
    "France": ["Normandie {item} SAS", "Beauce {item} SAS"], "India": ["Deccan {item} Pvt Ltd", "Punjab {item} Pvt Ltd"],
    "_other": ["Lowlands {item} B.V.", "Southern Cross {item} Ltd", "Paraná {item} Ltda", "Deccan {item} Pvt Ltd"],
}
EQUIPMENT = {  # step prefix -> equipment line in the production notes
    "Mashing": "2,000 L stainless mash tun with temperature control", "Filtration and vacuum": "plate filter and single-effect vacuum evaporator",
    "Roasting": "rotary drum roaster, 300 kg/h", "Cooking by extrusion": "twin-screw cooking extruder", "Drum drying": "steam-heated double drum dryer",
    "Simple grinding": "hammer mill", "Simple mixing": "ribbon blender, 500 kg", "Filling": "semi-automatic filling and sealing machine",
    "Cleaning": "vibrating sieve and destoner", "Simple sifting": "vibrating sieve",
}

FIRST = ["Adom", "Nkabom", "Sika", "Asase", "Nyame", "Ahomka", "Akwaaba", "Osei", "Kente", "Volta"]
SECOND = ["Foods", "Agro-Processing", "Nutrition", "Provisions", "Food Works", "Grains"]
TOWNS = ["Tema", "Kumasi", "Tamale", "Accra", "Takoradi", "Ho", "Koforidua"]
CONSIGNEE_CITIES = {"Nigeria": "Lagos", "Togo": "Lomé", "Côte d’Ivoire": "Abidjan", "Senegal": "Dakar",
                    "Kenya": "Nairobi", "Burkina Faso": "Ouagadougou"}
