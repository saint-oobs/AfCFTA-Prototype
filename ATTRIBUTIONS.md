# Attributions

## Libraries and runtime
| Item | Version | Use | Licence | Link |
|---|---|---|---|---|
| React / React DOM | 18.3.1 | UI | MIT | https://react.dev |
| React Router | 6.28.0 | Hash routing | MIT | https://reactrouter.com |
| Vite + @vitejs/plugin-react | 5.4.11 / 4.3.4 | Build | MIT | https://vitejs.dev |
| TypeScript | 5.6.3 | Types | Apache-2.0 | https://www.typescriptlang.org |
| Tailwind CSS, PostCSS, Autoprefixer | 3.4.15 / 8.4.49 / 10.4.20 | Styling | MIT | https://tailwindcss.com |
| anime.js | 3.2.2 | Stage transitions, result reveal, landing counters | MIT | https://animejs.com |
| clsx | 2.1.1 | Class names | MIT | https://github.com/lukeed/clsx |
| Pyodide | 0.26.4 (CDN, and npm for the CI parity check) | Python engine in the browser | MPL-2.0 | https://pyodide.org |
| Pillow | ≥10 | Rendering synthetic handwriting-style images | MIT-CMU (HPND) | https://python-pillow.org |
| pytest | ≥8 | Tests | MIT | https://pytest.org |

## Fonts
| Font | Use | Licence | Source |
|---|---|---|---|
| Public Sans (variable) | All website text | SIL OFL 1.1 | Fontsource `@fontsource-variable/public-sans` |
| Caveat | Synthetic handwriting-style document images (`generator/fonts/`, licence file included) | SIL OFL 1.1 | Fontsource `@fontsource/caveat` 5.0.8 |

## Rule texts
- *Agreement Establishing the African Continental Free Trade Area* – Laws.Africa and contributors, CC-BY ("Share widely and freely").
- *Appendix IV to Annex 2 on Rules of Origin as approved by the 12th AfCFTA Council of Ministers, December 2023*.
- *EX.CL/1329(XL)*, African Union Common Repository.

## Design components, 3D scenes and inspiration
| Source | Decision | Reason |
|---|---|---|
| Aceternity UI (ui.aceternity.com/components) | **Not used** | The licence forbids redistributing source files. |
| Skiper UI (skiper-ui.com/components) | **Not used** | Free-tier terms could not be confirmed; the terms of service reserve all rights and prohibit redistribution. |
| Spline community (community.spline.design) | **Not used** | No community file with a verifiable reuse licence was identified. The home page uses its own animated tile mosaic (`HeroMosaic.tsx`, anime.js). |
| recent.design | **Direction only** – no screenshots, layouts, logos or assets copied | General direction only (layout rhythm, whitespace). Crediting does not give a right to copy other designers' work, so nothing was copied. |

## Logo
The Tessera logo (nine tiles, accent tiles form a “T”) was drawn for this prototype as an inline SVG (`web/src/components/Logo.tsx`).

## Team
Oliwia Kosciolek, Apurv Sinha, Tereza Havlíčková, Ellinor Osvold, Vetle Nordli Strand (BI Norwegian Business School, AI for Business, Group 10).

## Generative AI
Code, rule extraction, synthetic data and draft documents were produced with Claude (Anthropic) under the group's direction and checked by the group (see `docs/appendix_b_draft.md`).
