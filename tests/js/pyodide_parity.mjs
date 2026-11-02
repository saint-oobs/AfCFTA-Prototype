// CI check: the same engine package gives identical results under Pyodide (browser runtime) and CPython.
import { loadPyodide } from 'pyodide'
import fs from 'node:fs'
const py = await loadPyodide()
const root = new URL('../../', import.meta.url).pathname
py.FS.mkdirTree('/home/pyodide/engine')
for (const f of fs.readdirSync(root + 'engine').filter(f => f.endsWith('.py'))) py.FS.writeFile('/home/pyodide/engine/' + f, fs.readFileSync(root + 'engine/' + f, 'utf8'))
py.globals.set('RULES_TEXT', fs.readFileSync(root + 'rules/rules.json', 'utf8'))
const ids = fs.readdirSync(root + 'web/public/data/cases').map(f => f.replace('.json', ''))
let ok = 0
for (const id of ids) {
  const rec = JSON.parse(fs.readFileSync(root + `web/public/data/cases/${id}.json`, 'utf8'))
  py.globals.set('CASE', JSON.stringify(rec.extracted))
  const out = JSON.parse(await py.runPythonAsync(`
import sys, json
sys.path.insert(0, '/home/pyodide')
from engine import load_rules, assess
json.dumps(assess(json.loads(CASE), load_rules(text=RULES_TEXT)))`))
  const same = JSON.stringify(out.outcome) === JSON.stringify(rec.result.outcome) && JSON.stringify(out.findings) === JSON.stringify(rec.result.findings)
  ok += same; if (!same) console.log('DIFF', id)
}
if (ok !== ids.length) process.exit(1)
console.log(`Pyodide ${py.runPython('import sys; sys.version.split()[0]')}: ${ok}/${ids.length} identical to CPython results`)
