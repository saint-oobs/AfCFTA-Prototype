"""Builds rules/rules.json. Every text below is copied verbatim from the attached
source files (typos kept). Run: python rules/build_rules.py"""
import json, pathlib

AGR = "Agreement_Establishing_the_African_Continental_Free_Trade_Area_1.pdf"
APPIV = "EN-APPENDIX-IV-AS-AT-COM-12-DECEMBER-2023_1.pdf"
EXCL = "EX_CL_1329_XL_E_1.pdf"

ST_AGR = "Agreement text as published by Laws.Africa ('as at 21 March 2018')"
ST_AGR_OUT = "Outstanding provision (footnoted in the Agreement text; see Annex 2 Art. 42)"
ST_APPIV = "Approved by the 12th AfCFTA Council of Ministers, December 2023"
ST_DRAFT = "Draft decision text, adoption not confirmed in attached sources"
D_AGR = "2018-03-21"; D_APPIV = "2023-12"; D_EXCL = "2022-01"

rules = []
def r(id, title, text, src, page, prov, date, status, behaviour, applied=True, notes=""):
    rules.append(dict(id=id, title=title, text=text, source_file=src, page=page,
        provision=prov, version_date=date, legal_status=status,
        engine_behaviour=behaviour, applied=applied, notes=notes))

# ---------------- Annex 2, Article 1 definitions ----------------
r("A2-1-h","Definition: Customs Value",
 "“Customs Value” means the value as determined in accordance with the WTO Agreement on implementation of Article VII of the General Agreement on Tariffs and Trade 1994 (WTO Agreement on customs valuation);",
 AGR,"12","Annex 2, Art. 1(h)",D_AGR,ST_AGR,"Defines the Customs Value field stored for every input.")
r("A2-1-k","Definition: Ex-works Price",
 "“Ex-works Price” means the price paid for the Product ex-works to the manufacturer in the States Party in whose undertaking the last working or processing is carried out, provided the price includes the value of all the Materials used minus any internal taxes paid which are, or may be, repaid when the Product obtained is exported;",
 AGR,"12","Annex 2, Art. 1(k)",D_AGR,ST_AGR,"Denominator of the tolerance share. Missing ex-works price -> 'Further information required (missing)' when the share is needed.")
r("A2-1-q","Definition: Material",
 "“Material” means any ingredient, raw material, component or part used in the Manufacture of a Product;",
 AGR,"12","Annex 2, Art. 1(q)",D_AGR,ST_AGR,"Every bill-of-materials line is treated as a Material.")
r("A2-1-x","Definition: Value Added",
 "\"Value Added\" means the difference between the ex-works price of a finished Product and the Customs Value of the Material imported from outside the State Parties and used in the production; [footnote 2: This definition is an outstanding provision]",
 AGR,"13","Annex 2, Art. 1(x)",D_AGR,ST_AGR_OUT,"Not used in the calculation (19.01 rule has no value-added test). Shown for reference only.",applied=False)
r("A2-1-y","Definition: Value of Materials",
 "“Value of Materials” means the Customs Value at the time of importation of the non-originating Materials used, or if this is not known and cannot be ascertained, the first ascertainable price paid for the Materials in any State Party.",
 AGR,"13","Annex 2, Art. 1(y)",D_AGR,ST_AGR,"Default valuation basis for the 15% tolerance (group decision Q1): Customs Value; if not known, the stated first ascertainable price in a State Party, labelled as fallback.")
# ---------------- Articles 4-6 ----------------
r("A2-4","Origin conferring criteria",
 "A Product shall be considered as originating from a State Party if it has: (a) been wholly obtained in that State Party within the meaning of Article 5 of this Annex; or (b) undergone substantial transformation in that State Party within the meaning of Article 6 of this Annex.",
 AGR,"13","Annex 2, Art. 4",D_AGR,ST_AGR,"Frames the assessment: 19.01 products are assessed under Art. 4(b) via Art. 6(2).")
r("A2-5-1","Wholly obtained products (chapeau and (b), (m))",
 "1. The following Products shall be considered as wholly obtained in a State Party when exported to another State Party: … (b) plants, including aquatic plants and plant Products, vegetables and fruits, grown or harvested therein; … (m) Goods produced therein exclusively from the Products specified in subparagraphs (a) to (l); …",
 AGR,"13–14","Annex 2, Art. 5(1)",D_AGR,ST_AGR,"Reference only: explains why a manufactured 19.01 preparation with imported inputs is not 'WP'.",notes="Excerpt; omitted sub-paragraphs marked with '…'.")
r("A2-6-1","Sufficiently worked or processed Products – criteria",
 "1. For purposes of Article 4(b) of this Annex, Products which are not wholly obtained are considered to be sufficiently worked or processed when they fulfil one of the following criteria: (a) Value Added; (b) non-originating Material content; (c) change in tariff Heading; or (d) specific processes.",
 AGR,"15","Annex 2, Art. 6(1)(a)–(d)",D_AGR,ST_AGR,"Art. 6(1)(c) change in tariff heading is the criterion type of the 19.01 rule -> Box 12 code SX.")
r("A2-6-2","Goods listed in Appendix IV",
 "2. Notwithstanding paragraph 1 of this Article, Goods listed in Appendix IV shall qualify as originating Goods if they satisfy the specific rules set out therein.",
 AGR,"15","Annex 2, Art. 6(2)",D_AGR,ST_AGR,"Routes the assessment to the Appendix IV row for heading 19.01.")
# ---------------- Article 7 ----------------
r("A2-7-1","Working or processing not conferring origin (chapeau)",
 "1. The following operations are insufficient to confer origin on a Product, whether or not the requirements of Article 4 of this Annex are satisfied:",
 AGR,"15","Annex 2, Art. 7(1)",D_AGR,ST_AGR,"Checked in every case, including when the 19.01 rule is met with or without the tolerance. If every production step maps to Art. 7(1)(a)–(n) (alone or combined, (o)), the result is 'Likely not to qualify' (critical).")
letters = {
 "a":"operations exclusively intended to preserve Products in good condition during storage and transportation;",
 "b":"breaking-up or assembly of packages;",
 "c":"washing, cleaning or operations to remove dust, oxide, oil, paint or other coverings from a Product;",
 "d":"simple ironing or pressing operations;",
 "e":"simple painting or polishing operations;",
 "f":"husking, partial or total bleaching, polishing or glazing of cereals and rice;",
 "g":"operations to colour sugar or form sugar lumps, partial or total milling of crystal sugar;",
 "h":"peeling, stoning or shelling of vegetables of Chapter 7, fruits of Chapter 8, nuts of Heading 08.01 or 08.02 or groundnuts of Heading 12.02, fruits, nuts or vegetables;",
 "i":"sharpening, simple grinding or simple cutting;",
 "j":"simple sifting, screening, sorting, classifying, grading or matching;",
 "k":"simple packaging operations, such as placing in bottles, cans, flasks, bags, cases, boxes or fixing on cards or boards;",
 "l":"affixing or printing marks, labels, logos, and other like distinguishing signs on the Products or their packaging;",
 "m":"simple mixing of Materials, whether or not of different kinds; which does not include an operation that causes a chemical reaction;",
 "n":"simple assembling of parts of articles to constitute a complete article;",
 "o":"a combination of two or more operations specified in sub-paragraphs (a) to (n); and",
 "p":"slaughter of animals.",
}
for k,v in letters.items():
    r(f"A2-7-1-{k}",f"Art. 7(1)({k})",f"({k}) {v}",AGR,"15","Annex 2, Art. "+f"7(1)({k})",D_AGR,ST_AGR,
      "Production steps mapped to this letter are 'listed operations' (see operation map)." if k not in "o" else
      "Applied when all production steps are listed operations of (a)–(n).")
r("A2-7-2","Food aid",
 "2. Notwithstanding any provision of this Annex, agricultural Products whether or not processed in anyway, obtained or partially obtained from Food Aid or monetisation or similar assistance measures, including arrangements based on non-commercial terms, shall not be considered as originating in a State Party.",
 AGR,"15","Annex 2, Art. 7(2)",D_AGR,ST_AGR,"Any input flagged as food aid -> critical finding, 'Likely not to qualify' (group decision Q10: 'partially obtained' read as covering the whole product).")
r("A2-7-3","Definition of 'simple'",
 "3. For purposes of paragraph 1 of this Article, an operation shall be considered simple when neither special skills, nor machines, apparatus nor tools especially produced or installed for those operations are required for their performance or when those skills, machines, apparatus or tools do not contribute to the Product’s essential characteristics or properties.",
 AGR,"16","Annex 2, Art. 7(3)",D_AGR,ST_AGR,"Basis for the operation map. Steps whose 'simple' character cannot be judged from the description are 'unclear' and routed to the adviser.")
# ---------------- Art 8, 10, 11 ----------------
r("A2-8","Cumulation of origin within the AfCFTA",
 "1. For purposes of implementing this Article, all State Parties shall be considered as a single Territory. 2. Raw Materials or semi-finished Goods originating in any of the State Parties and undergoing working or processing in another State Party, shall be deemed to have originated in the State Party where the final processing or manufacturing takes place. 3. Working or processing carried out in any of the State Parties shall be considered as having been carried out in the State Parties when the Materials undergo further working or processing in a State Party. 4. Notwithstanding paragraphs 1 and 2 of this Article, Products further manufactured in a State Party shall be considered as originating in a State Party where the last manufacturing process takes place provided that the last working or processing operations exceed those operations under Article 7 of this Annex.",
 AGR,"16","Annex 2, Art. 8",D_AGR,ST_AGR,"A 19.01 input originating in another State Party counts as originating only with proof under Art. 31(1). Box 12 code SC is suggested when this is relied on.")
r("A2-10","Unit of qualification",
 "1. The unit of qualification for the application of the provisions of this Annex shall be the particular Product, which is considered as a basic unit when determining classification. 2. For purposes of this Annex: (a) the tariff classification of a particular Product or Material shall be determined according to the Harmonized System; (b) a Product composed of a group or assembly of articles or components is classified pursuant to the terms of the HS under a single Heading or Sub-heading, the whole shall constitute a unit of qualification; and (c) where a shipment consists of a number of identical Products classified under the same Heading or Sub-heading of the Harmonised System, each Product shall be considered separately.",
 AGR,"16","Annex 2, Art. 10",D_AGR,ST_AGR,"One product per case; HS codes are taken as declared and checked for plausibility only.")
r("A2-11-1","Treatment of packing (separate determination)",
 "1. Where for purposes of assessing customs duties, a State Party treats Goods separately from their packing, it may also, in respect of its imports consigned from another State Party, determine separately the origin of such packing.",
 AGR,"17","Annex 2, Art. 11(1)",D_AGR,ST_AGR,"Limitation note: the importing State Party may determine packing origin separately; the tool cannot know this.")
r("A2-11-2","Treatment of packing (transport/storage packing)",
 "2. Where paragraph 1 of this Article is not applicable, packing shall be considered as forming a whole with the Goods and no part of any packing required for their transportation or storage shall be considered as having been imported from outside the State Party when determining the origin of the Goods as a whole.",
 AGR,"17","Annex 2, Art. 11(2)",D_AGR,ST_AGR,"Transport/storage packing is not treated as imported; no finding.")
r("A2-11-3","Treatment of packing (retail packing)",
 "3. For purposes of paragraph 2 of this Article, packing with which Goods are ordinarily sold at retail shall not be regarded as packing required for the transportation or storage of Goods.",
 AGR,"17","Annex 2, Art. 11(3)",D_AGR,ST_AGR,"Retail packing is treated as a Material. It is not classified in heading 19.01, so it cannot breach the 19.01 heading-change rule; unknown origin is a minor documentation finding (group decision Q4).")
# ---------------- Proof / evidence ----------------
r("A2-21-3","Documents proving originating status",
 "3. The Exporter applying for the issue of a Certificate of Origin shall submit at the request of the Designated Competent Authority of the exporting State Party where the Certificate of Origin is issued, all appropriate documents proving the originating status of the Products concerned as well as the fulfilment of the other requirements specified in this Annex.",
 AGR,"20","Annex 2, Art. 21(3)",D_AGR,ST_AGR,"Basis for evidence-completeness findings.")
r("A2-22","Supporting documents",
 "The documents, referred to in paragraph 3 of Article 21 of this Annex, to be submitted to the Designated Competent Authority of the exporting State Party may include documents relating to the following: (a) production processes carried out on the originating Product or on Materials used in the production of that Product; (b) purchase, cost, value of and payment for the Product; (c) origin, purchase, cost, value of and payment for all Materials, including neutral elements, used in the production of the Product; (d) shipment of the Product; and (e) any other documents that the Designated Competent Authority may consider necessary.",
 AGR,"20","Annex 2, Art. 22",D_AGR,ST_AGR,"Drives the readiness checklist.")
r("A2-31-1","Proof of origin of Materials from a State Party (cumulation)",
 "1. For purposes of paragraph 2 of Article 8 of this Annex, the proof of origin of the Materials coming from a State Party shall be given by a Certificate of Origin or an Origin Declaration in the form of Appendix I or II of this Annex.",
 AGR,"23","Annex 2, Art. 31(1)",D_AGR,ST_AGR,"A 19.01 input claimed as originating in another State Party without this proof -> 'Further information required (missing)', major.")
r("A2-31-2","Supplier or Producer's declaration (working or processing)",
 "2. For purposes of paragraph 3 of Article 8 of this Annex, the evidence of the working or processing shall be given by the supplier or Producer’s declaration, in the State Party in which the Materials are exported in the form set out in Appendix III of this Annex.",
 AGR,"23","Annex 2, Art. 31(2)",D_AGR,ST_AGR,"Accepted supporting declaration type for inputs.")
r("A2-31-3","Cumulation endorsement",
 "3. A Certificate of Origin issued pursuant to Article 8 of this Annex shall be endorsed with the word: “CUMULATION.” 4. The endorsement referred to in paragraph 3 of this Article shall be inserted in Box 3 of the Certificate of Origin.",
 AGR,"23","Annex 2, Art. 31(3)–(4)",D_AGR,ST_AGR,"Box 3 is completed by the issuing authority; the tool only notes that the endorsement may apply.")
r("A2-42","Transitional arrangements – outstanding issues",
 "1. State Parties agree that the following issues are outstanding: (a) Implementing decisions on the definitions of “Value Added” in Article 1 (x) and requirements for “their vessels” and “their factory ships” in Article 5(2) and criteria and issues pertaining to Special Economic Arrangements/Zones In Article 9 in Annex 2 on Rules of Origin; (b) Drafting of additional definitions in Annex 2 on Rules of Origin; (c) Drafting hybrid rules in Appendix IV to Annex 2 on the Rules of Origin; (d) Drafting Regulations for Goods produced under Special Economic Arrangements/Zones; (e) Drafting of additional provisions in Annex 2 on Rules of Origin on value tolerance, absorption principle and accounting segregation/GAAP; and (f) Drafting AfCFTA Rules of Origin Manuals/Guidelines. 2. The outstanding provisions referred to in paragraph 1 of this Article shall, upon adoption by the Assembly, form an integral part of this Annex. 3. Pending the adoption of the outstanding provisions, State Parties agree that the Rules of Origin in existing trade regimes shall be applicable.",
 AGR,"26","Annex 2, Art. 42",D_AGR,ST_AGR,"Used for status labels: value tolerance is listed as outstanding in 42(1)(e). Shown next to every tolerance result.")
r("A2-APPIII-A","Appendix III – Supplier or Producer's Declaration (preferential origin)",
 "I, the undersigned, declare that the Goods listed on invoice ______________ (1) were produced in ______________ (2) and satisfy the rules of origin governing preferential trade between the African Continental Free Trade Area State Parties. I undertake to make available to the Designated Competent Authority, if required, evidence in support of this declaration.",
 AGR,"30","Annex 2, Appendix III, Part A",D_AGR,ST_AGR,"Accepted evidence that a Ghanaian or State-Party input is originating.")
r("A2-APPIII-B","Appendix III – Supplier or Producer's Declaration (no preferential origin)",
 "I, the undersigned, declare that the Goods listed on this invoice ______________ (1) were produced in ______________ (2) and incorporate the following components or Materials which do not have an African Continental Free Trade Area origin for preferential trade:",
 AGR,"31","Annex 2, Appendix III, Part B",D_AGR,ST_AGR,"Evidence that an input is non-originating.")
# ---------------- Appendix I box notes ----------------
boxes = {
 "1":("27","The Exporter must be a natural or legal person ordinarily resident in a State Party or a person whose place of business is in a State Party. In addition, the Exporter’s registration number should be inserted, where applicable.","tool"),
 "2":("27","Insert the name and office address of the consignee in the State Party of destination.","tool"),
 "3":("27","To be completed by the issuing authority inserting one or more of the following endorsements where necessary: a) “Duplicate” … b) “Issued Retrospectively” … c) “Replacement” … d) “Cumulation”","authority"),
 "4":("27","Insert particulars of transport details for the vehicle, train, ship, aircraft or other vessel used in removing Goods from the last port in the exporting State Party.","tool"),
 "5":("27","a) Enter identifying marks and numbers on the packages against each Good being exported. b) If the packages are not marked, state “No Marks and Numbers” or “As Addressed”. c) For Goods in bulk that are not packed, insert “In Bulk”. d) The quantity stated must agree with the quantities on the invoice. e) Where both originating and non-originating Goods are packed together, describe only the originating Goods and add at the end “Part Contents Only”.","tool"),
 "6":("27","Insert serial numbers of invoices, their dates, values and Incoterms, issued for the Goods.","tool"),
 "7":("27","State the number of type of packaging containing the Goods.","tool"),
 "8":("27","The Goods must be identified by giving a reasonably full commercial description in order for the appropriate HS Code to be determined.","tool"),
 "9":("27","Insert the gross weight of the Goods that should correspond with the transporters’ documents.","tool"),
 "10":("27","State an additional statistical measure as may be applicable under the chosen HS Code","tool"),
 "11":("28","Enter the six-digit HS Code in respect of each line of Goods described in Box 8.","tool"),
 "12":("28","Insert the appropriate Origin Criteria Code applicable to the Goods being exported. WP Wholly produced (Article 5); SV Substantial transformation — Value Added Content (Article 6.1(a)); SM Substantial transformation — Material Content (Article 6.1(b)); SX Substantial transformation — Change of Tariff Heading (Article 6.1(c)); SP Substantial transformation — Process Rule (Article 6.1(d)); SC Substantial transformation — Cumulation; and state the States Parties with which Cumulation was used. (Article 8)","tool_indicative"),
 "13":("28","a) The Exporter, or the authorized representative, must complete all details required for a complete declaration of the correctness of the application for a Certificate of Origin. b) The signature must not be mechanically reproduced or made with a rubber stamp but can be electronically inserted or replaced with an electronic identifying code in accordance with the national laws of each State Party.","exporter"),
 "14":("28","This must be filled by the Designated Competent Authority in the State Party of export. …","authority"),
 "15":("28","The Customs Officer at the port of clearance or exit must insert the export document number, date and office of clearance as provided.","customs"),
}
for b,(pg,txt,who) in boxes.items():
    r(f"APPI-BOX-{b}",f"Appendix I – Box {b}",txt,AGR,pg,f"Annex 2, Appendix I, Box {b}",D_AGR,ST_AGR,
      {"tool":"Pre-filled in the draft compliance folder from case data.",
       "tool_indicative":"Pre-filled with an INDICATIVE suggestion only (SX or SC).",
       "exporter":"Not signed by the tool; listed in the readiness checklist for the exporter.",
       "authority":"Never completed by the tool (issuing authority).",
       "customs":"Never completed by the tool (Customs)."}[who])
r("APPI-NOTE","Appendix I – form not reproduced",
 "[Please note: The certificates have not been reproduced. Please refer to the publication document.]",
 AGR,"29","Annex 2, Appendix I",D_AGR,ST_AGR,"Folder labelled: 'based on the Appendix I box notes; the official form is not in the attached sources'.",
 notes="The Appendix I heading in the source reads '(Article 19(1)(a))'; cited as printed.")
# ---------------- Appendix IV ----------------
r("APPIV-N1.1","Introductory Note 1.1",
 "1.1 The rules set out in Column 3 of this Appendix are the minimum conditions required for the concerned Products to be considered as sufficiently worked or processed within the meaning of paragraph 2 of Article 6 of Annex 2 on Rules of Origin.",
 APPIV,"1","Appendix IV, Introductory Note 1.1",D_APPIV,ST_APPIV,"Explains that the 19.01 row is a minimum condition.")
r("APPIV-N2.1","Introductory Note 2.1",
 "2.1: The first two columns in the Appendix describe the Product obtained. The first column gives the Chapter, Heading or Sub-heading as it is used in the Harmonized System (HS). The second column gives the description of Goods as it is used in the HS for that Chapter, Heading or Sub-heading. For each entry in the first two columns a rule is specified in Column 3. Where, in some cases, the entry in the first column is preceded by an “ex”, this signifies that the rules in Column 3 apply only to the part of that Chapter, Heading or Sub-as described in Column 2.",
 APPIV,"1","Appendix IV, Introductory Note 2.1",D_APPIV,ST_APPIV,"Basis for using Column 2 descriptions as HS descriptions for input classification (group decision Q7).")
r("APPIV-N2.4","Introductory Note 2.4",
 "2.4: Where a Chapter, Heading or Sub-heading, in Column 1, or any text of this Appendix, is in square brackets that is an indication that the rule for that Chapter, Heading or Sub-heading in Column 3, or that text, is yet to be agreed by the AfCFTA Negotiating Institutions.",
 APPIV,"2","Appendix IV, Introductory Note 2.4",D_APPIV,ST_APPIV,"19.01 row is not in square brackets -> agreed.")
r("APPIV-N2.5","Introductory Note 2.5",
 "2.5: Where a Chapter, Heading or Sub-heading, in Column 1 has an asterisk, the value of non-originating materials will be automatically reduced from 60% to 55% threshold at the end of a five (5) year period starting 1 January 2021.",
 APPIV,"2","Appendix IV, Introductory Note 2.5",D_APPIV,ST_APPIV,"19.01 row has no asterisk -> not applicable.",applied=False)
r("APPIV-EXCH19","Ex-Chapter 19 row",
 "Ex-Chapter 19 | Preparations of cereals, flour, starch, or milk; pastrycooks products | Manufacture from Materials of any Heading other that of the Product provided that the wheat Products of Chapter 11 used must be originating",
 APPIV,"28","Appendix IV, Ex-Chapter 19",D_APPIV,"not applied – group decision","Not applied: the 19.01 row governs (group decision). Shown as an information note to the adviser when a Chapter 11 wheat input is present.",applied=False)
r("APPIV-1901","Heading 19.01 product-specific rule",
 "19.01 | Malt extract: food preparations of flour, groats, meal, starch or malt extract, not containing cocoa or containing less than 40 per cent by mass of cocoa calculated on a totally defatted basis, not elsewhere specified or included; food preparations of goods of headings 04.01 to 04.04, not containing cocoa or containing less than 5 per cent by mass of cocoa calculated on a totally defatted basis, not elsewhere specified or included | Manufacture from Materials of any Heading other that of the Product",
 APPIV,"29","Appendix IV, heading 19.01, Column 3",D_APPIV,ST_APPIV,"Retrieved by product heading 19.01. A non-originating Material classified in heading 19.01 breaches the rule unless the tolerance (EXCL-AN-3) applies. Applies to every subheading of 19.01.")
# ---------------- EX.CL/1329(XL) ----------------
r("EXCL-AN-1","Absorption Principle (draft)",
 "The value of the non-originating Materials used by the Producer in the production of a Product shall not include, for purposes of calculating the value of the product, the value of non-originating Materials used to produce originating Materials that are subsequently used in the production of the Product.",
 EXCL,"Annex p. 1","EX.CL/Draft/Dec…(XL) Annex, item 1",D_EXCL,ST_DRAFT,"Reference only: inputs declared originating are not decomposed.",applied=False)
r("EXCL-AN-2","Accounting Segregation (draft)",
 "Where originating and non-originating fungible Materials are used in the production of Products, the following methods shall be adopted in determining whether the Materials used are originating: a) physical separation of the Materials; or b) an inventory management method recognized in the Generally Accepted Accounting Principles of the exporting State Party, provided that the inventory management method selected is used for at least one (1) fiscal year.”",
 EXCL,"Annex p. 1","EX.CL/Draft/Dec…(XL) Annex, item 2",D_EXCL,ST_DRAFT,"Reference only: mixed-origin stock of the same input is flagged for the adviser.",applied=False)
r("EXCL-AN-3","Tolerance Rule (draft) – APPLIED",
 "1. Notwithstanding the provisions of Article 6, non-originating Materials which, according to the conditions set out in Appendix IV to this Annex shall not be used in the Manufacture of a given Product, may, nevertheless be used, provided that: b) Their total value does not exceed 15 per cent of the Ex-works Price of the final Product; c) The percentage given in paragraphs (a) of this paragraph shall not exceed any of the percentages for the maximum content of non-originating Materials as outlined in the Product Specific Rules laid out in Appendix IV. 1. Paragraph 1 of this Article shall not apply to Products falling within Chapters 50 through 63. 2. The tolerance in this Article shall be applied subject to the provisions of Article 7.",
 EXCL,"Annex p. 1","EX.CL/Draft/Dec…(XL) Annex, item 3 (lettering as printed: b), c) with no a))",D_EXCL,ST_DRAFT,
 "APPLIED, always on (group decision). Sum ALL non-originating 19.01 materials; share = sum / ex-works price compared exactly (sum*100 <= 15*price). Paragraph (c) has no effect for 19.01 (no maximum percentage in the row). Article 7 is checked in every case.",
 notes="Value tolerance is also listed as outstanding in Annex 2 Art. 42(1)(e).")
r("EXCL-AN-4","Additional introductory note on CTSH (draft)",
 "Pursuant to paragraph 2 of Article 6 of the Annex, in this Appendix the Change of Tariff Sub-Heading (CTSH) shall apply as follows: i. The non-originating materials used must be classified under a sub-heading other than that of the final product. ii. Sub-headings may appear in the same heading or in different headings.",
 EXCL,"Annex pp. 1–2","EX.CL/Draft/Dec…(XL) Annex, item 4",D_EXCL,ST_DRAFT,"Reference only: the 19.01 rule is a heading change, not CTSH.",applied=False)
r("EXCL-AN-6","Definition of Value Added (draft)",
 "Value Added means the difference between the ex-works price of a finished Product and the Customs Value of the Material imported from outside the State Parties and used in the Production.",
 EXCL,"Annex p. 2","EX.CL/Draft/Dec…(XL) Annex, item 6",D_EXCL,ST_DRAFT,"Reference only.",applied=False)
r("EXCL-AN-7","FOB as basis of calculation of VNOM (draft)",
 "FOB shall be the basis of the calculation of the Value of Non-originating materials (VNOM).",
 EXCL,"Annex p. 2","EX.CL/Draft/Dec…(XL) Annex, item 7",D_EXCL,ST_DRAFT,"Alternative valuation basis. Computed alongside Customs Value; shown when it changes the outcome (group decision Q1).",applied=False)
r("EXCL-DD-7","State Party list (draft decision, Jan 2022)",
 "REITERATES its congratulations to the thirty nine (39) State Parties who deposited their instruments of ratification of the AfCFTA Agreement with the Chairperson of the Commission, namely: Angola, Burkina Faso, Cameroon, Central African Republic, Chad, Côte d’Ivoire, Congo, Djibouti, Egypt, Eswatini, Ethiopia, Equatorial Guinea, Gabon, The Gambia, Ghana, Guinea, Kenya, Lesotho, Mali, Mauritania, Mauritius, Namibia, Niger, Nigeria, Rwanda, Saharawi Arab Democratic Republic, Sao Tome and Principe, Senegal, Sierra Leone, South Africa, Togo, Tunisia, Uganda and Zimbabwe;",
 EXCL,"Draft decision p. 1","EX.CL/Draft/Dec…(XL), para. 7",D_EXCL,ST_DRAFT,"Only the 34 named countries are used as State Party suppliers (group decision Q2). Dated January 2022; may be outdated.",
 notes="Text says 39 but names 34; para. 6 adds Burundi and Seychelles; report para. 3 says 40. Not resolved in attached sources.")
r("EXCL-DD-23","Provisional application of REC rules (draft decision)",
 "ENDORSES the Guidelines for the Provisional Application of Rules of Origin for the remaining outstanding tariff lines in accordance with existing trade regimes or Regional Economic Communities, pending the adoption of all outstanding issues in the Rules of Origin negotiations, in line with Article 42(3) of Annex 2 of the Protocol on Trade in Goods",
 EXCL,"Draft decision p. 4","EX.CL/Draft/Dec…(XL), para. 23",D_EXCL,ST_DRAFT,"Limitation note only.",applied=False)

STATE_PARTIES = ["Angola","Burkina Faso","Cameroon","Central African Republic","Chad","Côte d’Ivoire","Congo","Djibouti","Egypt","Eswatini","Ethiopia","Equatorial Guinea","Gabon","The Gambia","Ghana","Guinea","Kenya","Lesotho","Mali","Mauritania","Mauritius","Namibia","Niger","Nigeria","Rwanda","Saharawi Arab Democratic Republic","Sao Tome and Principe","Senegal","Sierra Leone","South Africa","Togo","Tunisia","Uganda","Zimbabwe"]

# Group interpretation: mapping of production operations to Art. 7(1).
OPERATION_MAP = [
 # code, label, status, art7 letter
 ("preserve_storage","Preservation for storage/transport only","listed","a"),
 ("break_up_packages","Breaking-up or assembly of packages","listed","b"),
 ("cleaning_washing","Washing / cleaning","listed","c"),
 ("husking_polishing_cereals","Husking / polishing of cereals","listed","f"),
 ("simple_grinding","Simple grinding (no special installation)","listed","i"),
 ("simple_sifting_sorting","Simple sifting / sorting / grading","listed","j"),
 ("simple_packaging","Simple packaging (bagging, bottling)","listed","k"),
 ("labelling","Labelling / marking","listed","l"),
 ("simple_mixing","Simple mixing / blending","listed","m"),
 ("mashing_enzymatic","Mashing / enzymatic conversion of malt","not_listed",None),
 ("evaporation_concentration","Vacuum evaporation / concentration","not_listed",None),
 ("roasting_toasting","Roasting / toasting","not_listed",None),
 ("cooking_extrusion","Cooking / extrusion cooking","not_listed",None),
 ("drying_drum_spray","Drum or spray drying of a cooked preparation","not_listed",None),
 ("fermentation","Fermentation","not_listed",None),
 ("industrial_milling","Milling on specially installed equipment","unclear",None),
 ("unspecified_processing","Unspecified 'processing' / 'preparation'","unclear",None),
]

# HS references for inputs (group decision Q7): Appendix IV Column 1-2, used as HS descriptions per Note 2.1.
HS_REFERENCE = [
 {"code":"Chapter 4","level":"chapter","description":"Dairy produce; birds' eggs; natural honey; edible Products of animal origin, not elsewhere specified or included","page":"16"},
 {"code":"04.01","level":"heading","description":"Milk and cream, not concentrated nor containing added sugar or other sweetening matter","page":"17"},
 {"code":"Chapter 10","level":"chapter","description":"Cereals","page":"19"},
 {"code":"Ex-Chapter 11","level":"chapter","description":"Products of the milling industry; malt; starches; inulin; wheat gluten","page":"19"},
 {"code":"11.01","level":"heading","description":"Wheat or meslin flour","page":"19"},
 {"code":"11.04","level":"heading","description":"Cereal grains otherwise worked (for example, hulled, rolled, flaked, pearled, sliced or kibbled) (excluding rice of Heading 10.06); germ of cereals, whole, rolled, flaked or ground","page":"20"},
 {"code":"11.07","level":"heading","description":"Malt, whether or not roasted","page":"20"},
 {"code":"Chapter 12","level":"chapter","description":"Oil seeds and oleaginous fruits; miscellaneous grains, seeds and fruit; industrial or medicinal plants; straw and fodder","page":"21"},
 {"code":"Chapter 17","level":"chapter","description":"Sugars and sugar confectionery","page":"27"},
 {"code":"17.02","level":"heading","description":"Other sugars, including chemically pure lactose, maltose, glucose and fructose, in solid form; sugar syrups not containing added flavouring or colouring matter; artificial honey, whether or not mixed with natural honey; caramel","page":"27–28"},
 {"code":"21.02","level":"heading","description":"Yeasts (active or inactive); other single-cell micro-organisms, dead (but not including vaccines of Heading 30.02); prepared baking powders","page":"32"},
 {"code":"19.01","level":"heading","description":"Malt extract: food preparations of flour, groats, meal, starch or malt extract, … not elsewhere specified or included","page":"29"},
 {"code":"Ex-Chapter 39","level":"chapter","description":"Plastics and articles thereof","page":"48"},
 {"code":"Chapter 48","level":"chapter","description":"Paper and paperboard; articles of paper pulp, of paper or of paperboard","page":"55"},
]

decisions = [
 {"id":"GD-1","decision":"The 15% tolerance (EXCL-AN-3) is applied, always on, although it is draft decision text.","rule_ids":["EXCL-AN-3","A2-42"],"source":"Group decision (confirmed by project lead, 2026-11-01)"},
 {"id":"GD-2","decision":"The Ex-Chapter 19 wheat condition is not applied because the 19.01 row governs; shown as an information note.","rule_ids":["APPIV-EXCH19"],"source":"Group decision"},
 {"id":"GD-Q1","decision":"Valuation basis for the tolerance: Customs Value (Art. 1(y)); FOB (EXCL-AN-7) computed alongside and shown when it changes the outcome.","rule_ids":["A2-1-y","EXCL-AN-7"],"source":"Group decision Q1"},
 {"id":"GD-Q2","decision":"State Party suppliers are drawn only from the 34 countries named in EX.CL draft decision para. 7; non-State-Party suppliers are non-African countries.","rule_ids":["EXCL-DD-7"],"source":"Group decision Q2"},
 {"id":"GD-Q4","decision":"Severity: critical = rule text says the certificate would fail; major = cannot be assessed without new evidence; minor = resolvable form or consistency issue.","rule_ids":[],"source":"Group decision Q4"},
 {"id":"GD-Q5","decision":"A determinate critical failure overrides missing data; missing items are still listed.","rule_ids":[],"source":"Group decision Q5"},
 {"id":"GD-Q6","decision":"Operation map (Art. 7(1) letters vs. not-listed vs. unclear) is a group interpretation of Art. 7(1) and 7(3).","rule_ids":["A2-7-1","A2-7-3"],"source":"Group decision Q6"},
 {"id":"GD-Q7","decision":"Input HS codes use Appendix IV Column 1–2 descriptions (Note 2.1) at heading level where a row exists, otherwise chapter level.","rule_ids":["APPIV-N2.1"],"source":"Group decision Q7"},
 {"id":"GD-Q10","decision":"Any food-aid input makes the product fail (Art. 7(2) 'partially obtained').","rule_ids":["A2-7-2"],"source":"Group decision Q10"},
 {"id":"GD-Q11","decision":"All values in GHS; mixed currency on a relevant input = contradictory (no exchange-rate source).","rule_ids":["A2-1-y"],"source":"Group decision Q11"},
 {"id":"GD-Q12","decision":"Box 12 suggestion: SX; SC when a State-Party 19.01 input is counted as originating. Always indicative.","rule_ids":["APPI-BOX-12","A2-8"],"source":"Group decision Q12"},
 {"id":"GD-Q13","decision":"Repeated error = same error type on same field logged twice or more -> bug report to model development team.","rule_ids":[],"source":"Group decision Q13; Service_Blueprint_1.pdf"},
]

doc = {
 "schema_version":"1.0",
 "rulebase_version":"1.1.0",
 "compiled":"2026-11-01",
 "product_heading":"19.01",
 "sources":{
  AGR:{"title":"Agreement Establishing the African Continental Free Trade Area (Laws.Africa, as at 21 March 2018)","licence":"CC-BY (Laws.Africa and contributors)"},
  APPIV:{"title":"Appendix IV to Annex 2 on Rules of Origin as approved by the 12th AfCFTA Council of Ministers, December 2023"},
  EXCL:{"title":"EX.CL/1329(XL) Report of the Secretary General of the AfCFTA, January 2022, incl. draft decision and annex"},
 },
 "parameters":{
  "tolerance":{"rule_id":"EXCL-AN-3","percent":"15","base":"ex_works_price","comparison":"<=","excluded_chapters":"50-63","always_on":True},
  "valuation_basis_default":"customs_value",
  "valuation_basis_alternative":"fob",
  "currency":"GHS",
  "repeated_error_threshold":2,
 },
 "rules":rules,
 "state_parties":{"rule_id":"EXCL-DD-7","countries":STATE_PARTIES},
 "operation_map":[{"code":c,"label":l,"status":s,"art7_letter":a,"rule_id":(f"A2-7-1-{a}" if a else "A2-7-3"),"legal_status":"group interpretation"} for c,l,s,a in OPERATION_MAP],
 "hs_reference":[dict(h, source_file=APPIV, rule_id="APPIV-N2.1") for h in HS_REFERENCE],
 "decisions":decisions,
}
out = pathlib.Path(__file__).parent / "rules.json"
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote {out} with {len(rules)} rules")
