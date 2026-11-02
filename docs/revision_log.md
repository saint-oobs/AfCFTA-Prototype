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
