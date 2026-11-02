// Copies the SAME Python engine package and rules.json into public/py so the browser runs it in Pyodide.
import { cpSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs'
const out = new URL('../public/py/', import.meta.url)
mkdirSync(new URL('engine/', out), { recursive: true })
const files = readdirSync(new URL('../../engine/', import.meta.url)).filter(f => f.endsWith('.py'))
for (const f of files) cpSync(new URL(`../../engine/${f}`, import.meta.url), new URL(`engine/${f}`, out))
cpSync(new URL('../../rules/rules.json', import.meta.url), new URL('rules.json', out))
writeFileSync(new URL('manifest.json', out), JSON.stringify({ files }))
console.log('copied engine files:', files.join(', '))
