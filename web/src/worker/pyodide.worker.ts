/// <reference lib="webworker" />
// Runs the SAME Python engine package (engine/*.py) with rules.json in Pyodide.
declare const loadPyodide: any
declare function importScripts(...urls: string[]): void
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/'
let py: any = null

async function init(base: string) {
  importScripts(PYODIDE + 'pyodide.js')
  py = await loadPyodide({ indexURL: PYODIDE })
  const manifest = await (await fetch(base + 'py/manifest.json')).json()
  py.FS.mkdirTree('/home/pyodide/engine')
  for (const f of manifest.files) {
    const src = await (await fetch(base + 'py/engine/' + f)).text()
    py.FS.writeFile('/home/pyodide/engine/' + f, src)
  }
  const rules = await (await fetch(base + 'py/rules.json')).text()
  py.globals.set('RULES_TEXT', rules)
  await py.runPythonAsync(`
import sys, json
sys.path.insert(0, '/home/pyodide')
from engine import load_rules, assess, check_citations, ENGINE_VERSION
RB = load_rules(text=RULES_TEXT)
def run(case_json, basis=None):
    return json.dumps(assess(json.loads(case_json), RB, basis))
def cite(text):
    return json.dumps(check_citations(text, RB))
`)
  return py.globals.get('ENGINE_VERSION')
}

self.onmessage = async (e: MessageEvent) => {
  const { id, type, payload } = e.data
  try {
    if (type === 'init') {
      const v = await init(payload.base)
      ;(self as any).postMessage({ id, ok: true, result: { version: v, python: py.runPython('import sys; sys.version.split()[0]') } })
    } else if (type === 'assess') {
      const out = py.globals.get('run')(JSON.stringify(payload.case), payload.basis ?? null)
      ;(self as any).postMessage({ id, ok: true, result: JSON.parse(out) })
    } else if (type === 'cite') {
      ;(self as any).postMessage({ id, ok: true, result: JSON.parse(py.globals.get('cite')(payload.text)) })
    }
  } catch (err: any) {
    ;(self as any).postMessage({ id, ok: false, error: String(err?.message || err) })
  }
}
