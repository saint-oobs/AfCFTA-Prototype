# Errors, revisions and versions

| ID | Component | Found by | Error | Change | Before | After |
|---|---|---|---|---|---|---|
| D-1 | Engine 1.0.0 (before release) | Unit test | A currency mismatch gave two reasons: 'contradictory' and 'missing'. | A currency mismatch now gives one reason: 'contradictory'. | Further information required (contradictory, missing) | Further information required (contradictory) |
| R1 | Adapter stub 1.0.0 → 1.1.0 | Run 1 of the case pack | Two ingredient lines had the same description. The stub linked both supplier documents to the first line. The second line lost its proof of origin and got a false conflict. | The stub links a supplier document to a line by supplier name and goods. If the link is not unique, the document stays unlinked. | T3d: Further information required (contradictory) | T3d: Likely not to qualify |
| R2 | Engine 1.0.0 → 1.1.0 and answer key (K1) | Run 2 of the case pack | When the HS code was in doubt, the engine stopped before the food-aid check. Art. 7(2) applies 'notwithstanding any provision', so the check must always run. | The food-aid check and the form checks run in all cases. The answer key was corrected in the same way (K1). Two group members must confirm K1. | E03: food-aid finding missing | E03: Likely not to qualify, both findings shown |
| R3 | Adapter stub explanation 1.1.0 | Review of test 5 output | With a value that cannot be read, the summary said '0.000% of the ex-works price'. This can mislead the SME. | The summary now says that the share cannot be calculated yet. | 'make up 0.000% of the ex-works price' | 'The share cannot be calculated yet' |

### Version log

| Version | Change |
|---|---|
| Rule base 1.0.0 → 1.1.0 | Added heading 21.02 (baking powder) to the HS reference list. |
| Engine 1.1.0 → 1.2.0 | Requirement table written in plain language. Each finding has an action for the SME. No rule logic changed. |
| Adapter stub 1.1.0 → 1.2.0 | Summary for the SME in plain language. Product description snippets for the adviser. French production steps translated. |
| Generator 1.0.0 → 1.1.0 | Four products in three subheadings: 1901.10 infant cereal, 1901.20 malted bread mix, 1901.90 malt extract and millet porridge mix. |

## v4 (2026-11-06) – group feedback round 4
- Overview: new stage texts (output, human decision, feedback), plain-language rule cards without citations, rule-data version box.
- Documents: no watermark line, no certificates of origin (AfCFTA suppliers now give an Appendix III supplier declaration), packaging table with headers and without HS codes, production notes as a table, aligned costing sheet and invoice.
- Ingredient HS codes are six-digit HS 2022 subheadings (e.g. millet 1008.29, sugar 1701.99, milk powder 0402.10) instead of chapter-level codes. Group to verify.
- "Simple operations" renamed "eligible manufacturing processes under AfCFTA guidelines" (wording only; no rule change). Engine 1.3.0, stub 1.3.0, generator 1.3.0.
- Manual entry opens an empty form; the check runs on the typed data.
- Adviser view ends after the technical overview. Test log: misc set moved up, assessment accuracy = confusion matrix, severity legend, four record types.

## v4.1 (2026-11-06)
- Overview: "How Tessera works", no rule-data box, stage 6 tasks = error log, bug reports, support insights.
- All tables and document fields left-aligned with one label width per document.
- Rule data shown as "AfCFTA guidelines as of 1 November 2026" (date of rules.json "compiled").
- Proof-of-origin sentence names the ingredients. Test log: one row per case, red/orange/yellow severity palette, record-type matrix.

## v4.2 (2026-11-06)
- Test order: 1 Typical (malt extract, T1) · 2 Failure (millet porridge mix, T2, former T4) · 3 Edge (bread mix, T3a–d) · 4 Edge / difficult: HS code in doubt (cassava flour declared 1901.20, T4, replaces former E08) · 5 Key assumption (infant cereal, T5a/b).
- Former T2 (typical infant cereal) removed; miscellaneous set renumbered E01–E11. New recipe `cassava_flour`. Fixed key updated by hand (T4 derivation).
