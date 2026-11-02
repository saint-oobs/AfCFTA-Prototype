import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import anime from 'animejs'
import { getCase, getIndex, getRules } from '../lib/data'
import { initEngine, runEngine } from '../lib/engine'
import { log } from '../lib/log'
import { reduced, reveal } from '../lib/motion'
import { smeSummary } from '../lib/summary'
import { PageHead } from '../components/ui'
import { AiTask, Documents, ModelTab, Upload } from '../components/Inputs'
import { SummaryStrip } from '../components/Result'
import { AdviserView } from '../components/Adviser'
import SmeView from '../components/SmeView'
import RuleDrawer from '../components/RuleDrawer'
import { ArrowLeft, ArrowRight } from '../components/icons'

const TABS = [['upload', 'Upload'], ['inputs', '1 Inputs'], ['ai', '2 AI task'], ['model', '3 Model'], ['adviser', '4 Adviser view'], ['sme', '5 SME view']] as const
const TEST_LABEL: Record<string, string> = {
  '1': 'Test 1 – Typical: malt extract (1901.90)', '2': 'Test 2 – Typical: infant cereal (1901.10)',
  '3': 'Test 3 – Edge: 15% limit, bread mix (1901.20)', '4': 'Test 4 – Failure: simple operations (1901.90)',
  '5': 'Test 5 – Key assumption: handwritten records (1901.10)', eval: 'Evaluation set – missing and contradictory information',
}
const CASE_LABEL: Record<string, string> = {
  T1: 'T1', T2: 'T2', T3a: 'T3a – 14.9%', T3b: 'T3b – exactly 15.0%', T3c: 'T3c – 15.1%', T3d: 'T3d – two lots, 16.0%', T4: 'T4',
  T5a: 'T5a – all values readable', T5b: 'T5b – one value smudged',
}
let loadErrorLogged = false

export default function Navigator() {
  const { caseId = 'T1', tab = 'inputs' } = useParams()
  const nav = useNavigate()
  const [index, setIndex] = useState<any>(null)
  const [rules, setRules] = useState<any>(null)
  const [rec, setRec] = useState<any>(null)
  const [extracted, setExtracted] = useState<any>(null)
  const [result, setResult] = useState<any>(null)
  const [summary, setSummary] = useState<string>('')
  const [ready, setReady] = useState(false)
  const [rule, setRule] = useState<any>(null)
  const [editing, setEditing] = useState(false)
  const bar = useRef<HTMLDivElement>(null), panel = useRef<HTMLDivElement>(null)
  const tabIdx = Math.max(0, TABS.findIndex(t => t[0] === tab))

  useEffect(() => { getIndex().then(setIndex); getRules().then(setRules) }, [])
  useEffect(() => {
    initEngine().then(() => setReady(true)).catch(e => {
      if (!loadErrorLogged) { loadErrorLogged = true; log.add({ case_id: '-', kind: 'error', error_type: 'engine_load', detail: `Rule engine did not load in the browser; saved results used. ${String(e.message || e)}` }) }
    })
  }, [])
  useEffect(() => {
    getCase(caseId).then(r => { setRec(r); setExtracted(structuredClone(r.extracted)); setResult(r.result); setSummary(r.explanation.text); setEditing(false) }).catch(() => setRec(null))
  }, [caseId])
  useEffect(() => { if (ready && rec) run(rec.extracted) }, [ready, rec])
  useEffect(() => {
    const w = `${((tabIdx + 1) / TABS.length) * 100}%`
    if (bar.current) { if (reduced()) bar.current.style.width = w; else anime({ targets: bar.current, width: w, duration: 450, easing: 'easeOutCubic' }) }
    reveal(panel.current)
  }, [tabIdx, caseId])

  async function run(c: any) {
    try { const r = await runEngine({ ...c, case_id: caseId }); setResult(r); setSummary(smeSummary(r)) }
    catch (e: any) { log.add({ case_id: caseId, kind: 'error', error_type: 'engine', detail: `Rule engine error: ${String(e.message || e)}` }) }
  }
  const caseInfo = index?.cases.find((c: any) => c.case_id === caseId)
  const test = caseInfo ? (caseInfo.set === 'eval' ? 'eval' : String(caseInfo.test)) : '1'
  const casesOfTest = useMemo(() => (index?.cases ?? []).filter((c: any) => test === 'eval' ? c.set === 'eval' : String(c.test) === test && c.set === 'fixed'), [index, test])
  const openRule = (id: string) => setRule(rules?.rules.find((r: any) => r.id === id) ?? null)
  const go = (t: string, c = caseId) => nav(`/navigator/${c}/${t}`)

  return (
    <>
      <PageHead title="Navigator" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 space-y-4">
        <div className="card p-4 flex flex-wrap items-end gap-4">
          <label className="text-sm"><span className="label block mb-1">Test</span>
            <select className="field" value={test} onChange={e => {
              const t = e.target.value; const first = (index?.cases ?? []).find((c: any) => t === 'eval' ? c.set === 'eval' : String(c.test) === t && c.set === 'fixed')
              if (first) go(tab, first.case_id)
            }}>{Object.entries(TEST_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
          <label className="text-sm"><span className="label block mb-1">Case</span>
            <select className="field" value={caseId} onChange={e => go(tab, e.target.value)}>
              {casesOfTest.map((c: any) => <option key={c.case_id} value={c.case_id}>{CASE_LABEL[c.case_id] ?? `${c.case_id} – ${c.scenario?.split('.')[0] ?? c.product}`}</option>)}
            </select></label>
          <Link to={`/logic/${caseId}`} className="btn ml-auto">Show the logic</Link>
        </div>
        {result && <SummaryStrip result={result} extracted={extracted} scenario={rec?.meta?.spec?.scenario} />}

        <div className="sticky top-14 z-20 bg-bg/95 backdrop-blur pt-2 no-print">
          <div role="tablist" aria-label="Stages" className="flex gap-1 overflow-x-auto">
            {TABS.map(([k, l]) => (
              <button key={k} role="tab" aria-selected={tab === k} onClick={() => go(k)}
                className={`shrink-0 rounded-t-md px-3 py-2 text-sm font-medium border-b-2 transition-colors ${tab === k ? 'border-accent text-accent bg-accent-soft' : 'border-transparent text-muted hover:text-ink'}`}>{l}</button>))}
          </div>
          <div className="h-1 bg-line rounded" aria-hidden><div ref={bar} className="h-1 bg-accent rounded" style={{ width: `${((tabIdx + 1) / TABS.length) * 100}%` }} /></div>
        </div>

        <div ref={panel} role="tabpanel" className="space-y-4">
          {!rec || !result ? <p className="note">Loading…</p> : <>
            {tab === 'upload' && <Upload onSample={() => go('inputs', 'T5a')} onManual={() => { setEditing(true); go('model') }} />}
            {tab === 'inputs' && <Documents rec={rec} />}
            {tab === 'ai' && <AiTask rec={rec} />}
            {tab === 'model' && <ModelTab rec={rec} extracted={extracted} setExtracted={setExtracted} canRun={ready} rules={rules} editing={editing} setEditing={setEditing}
              onRun={() => { log.add({ case_id: caseId, kind: 'rerun', detail: 'New run after manual entry' }); run(extracted); go('adviser') }} />}
            {tab === 'adviser' && <AdviserView caseId={caseId} rec={rec} extracted={extracted} result={result} canRun={ready} onRule={openRule}
              rerun={async (hs) => { const c = structuredClone(extracted); c.product.declared_hs = hs; c.product.hs_doubt = false; setExtracted(c); await run(c) }} />}
            {tab === 'sme' && <SmeView caseId={caseId} extracted={extracted} result={result} summary={summary} />}
            <div className="flex justify-between no-print">
              {tabIdx > 0 ? <button className="btn" onClick={() => go(TABS[tabIdx - 1][0])}><ArrowLeft />{TABS[tabIdx - 1][1]}</button> : <span />}
              {tabIdx < TABS.length - 1 && <button className="btn-primary" onClick={() => go(TABS[tabIdx + 1][0])}>{TABS[tabIdx + 1][1]}<ArrowRight /></button>}
            </div>
          </>}
        </div>
      </div>
      <RuleDrawer rule={rule} onClose={() => setRule(null)} />
    </>
  )
}
