import { useEffect, useState, useSyncExternalStore } from 'react'
import { Section, Tag } from './ui'
import { log } from '../lib/log'
import { docName } from './Inputs'
import { Findings, InfoRequest, Requirements, TolerancePanel } from './Result'
import { Check, Message, Refresh, Send } from './icons'

const THRESHOLD = 2 // rules.json parameters.repeated_error_threshold

export function useDecision(caseId: string) {
  const events = useSyncExternalStore(log.subscribe, log.all)
  return [...events].reverse().find(e => e.case_id === caseId && ['approved', 'missing_info', 'clarification'].includes(e.kind))
}

type Ans = 'yes' | 'no' | null

export function AdviserView({ caseId, rec, extracted, result, canRun, rerun, onRule }: {
  caseId: string; rec: any; extracted: any; result: any; canRun: boolean; rerun: (hs: string) => Promise<void>; onRule: (id: string) => void }) {
  const [citation, setCitation] = useState<Ans>(null)
  const [correct, setCorrect] = useState<Ans>(null)
  const [hs, setHs] = useState('')
  const [bug, setBug] = useState<null | { released: boolean }>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const events = useSyncExternalStore(log.subscribe, log.all)
  useEffect(() => { setCitation(null); setCorrect(null); setHs(''); setMsg(null); setBug(null) }, [caseId, result])
  const tags = (rec?.adapter?.field_tags || []).filter((t: any) => t.field.startsWith('product.'))
  const declared = extracted?.product?.declared_hs ?? '—'
  const validHs = /^\d{4}\.?\d{2}$/.test(hs)

  let action: { label: string; Icon: any; run: () => void; disabled?: boolean } | null = null
  if (citation === 'no') action = { label: 'Ask the SME for more information', Icon: Message, run: () => done('clarification', 'Asked the SME for more information on the HS code', 'Request sent to the SME.') }
  else if (citation === 'yes' && correct === 'no') action = { label: validHs ? `Run the model again with HS ${hs}` : 'Run the model again with the correct HS code', Icon: Refresh, run: wrongHs, disabled: !validHs }
  else if (citation === 'yes' && correct === 'yes') action = { label: 'Approve and send to the SME', Icon: Send, run: () => done('approved', `Approved: ${result.outcome.label}`, 'Result sent to the SME.') }

  function done(kind: any, detail: string, text: string) { log.add({ case_id: caseId, kind, detail }); setMsg(text) }
  async function wrongHs() {
    const before = log.count('wrong_hs', 'product.declared_hs')
    log.add({ case_id: caseId, kind: 'override', error_type: 'wrong_hs', field: 'product.declared_hs', detail: `HS ${declared} changed to ${hs}` })
    if (before + 1 >= THRESHOLD) {
      log.add({ case_id: caseId, kind: 'bug_report', error_type: 'wrong_hs', field: 'product.declared_hs', detail: `Same error ${before + 1} times: product HS code` })
      setBug({ released: false }); return
    }
    await doRerun()
  }
  async function doRerun() {
    if (!canRun) { setMsg('The correction is recorded. The model cannot run again in this browser.'); return }
    log.add({ case_id: caseId, kind: 'rerun', detail: `New run with HS ${hs}` })
    await rerun(hs); setCitation(null); setCorrect(null); setMsg('The model ran again with the corrected HS code.')
  }
  const yesNo = (v: Ans, set: (a: Ans) => void, label: string) => (
    <div className="flex flex-wrap items-center gap-2 mt-3"><span className="text-sm font-medium mr-1">{label}</span>
      {(['yes', 'no'] as const).map(a => <button key={a} aria-pressed={v === a} onClick={() => { set(a); setMsg(null) }}
        className={`btn !py-1.5 ${v === a ? '!border-accent !bg-accent-soft !text-accent' : ''}`}>{a === 'yes' ? 'Yes' : 'No'}</button>)}</div>)

  const errors = events.filter(e => e.kind === 'error' && (e.case_id === caseId || e.case_id === '-'))
  const count = (s: string) => (rec?.adapter?.field_tags || []).filter((t: any) => t.status === s).length
  const unmatched = (rec?.adapter?.field_tags || []).filter((t: any) => String(t.status).startsWith('unmatched'))
  const conflicts = (extracted?.inputs || []).filter((i: any) => i.conflicts?.length).length

  return (
    <div className="space-y-4">
      <Section kicker="Step 1" title="Check the HS code">
        <div className="grid md:grid-cols-[200px_1fr] gap-5">
          <div className="rounded-lg bg-panel p-4"><p className="label">Identified HS code</p><p className="text-3xl font-semibold tabular-nums mt-1">{declared}</p>
            {extracted?.product?.hs_doubt && <p className="mt-2 text-sm text-major">Flagged: {extracted.product.hs_doubt_reason}</p>}</div>
          <div><p className="label mb-2">Citations from the SME's documents</p>
            <ul className="space-y-2 text-sm">{tags.map((t: any, i: number) => (
              <li key={i} className="border-l-2 border-accent pl-3">“{t.snippet}”<span className="block note">{docName(rec, t.doc_id)}</span></li>))}</ul></div>
        </div>
        {yesNo(citation, a => { setCitation(a); setCorrect(null) }, 'Is the citation enough to verify the HS code?')}
        {citation === 'yes' && <>
          {yesNo(correct, setCorrect, 'Is the HS code correct?')}
          {correct === 'no' && <label className="mt-3 flex flex-wrap items-center gap-2 text-sm">Correct HS code
            <input className="field w-32" placeholder="1901.90" value={hs} onChange={e => setHs(e.target.value)} /></label>}
        </>}
      </Section>

      <Section kicker="Step 2" title="Action">
        {!action && <p className="note">Answer the questions in step 1.</p>}
        {action && !bug && <button className="btn-primary" disabled={action.disabled} onClick={action.run}><action.Icon />{action.label}</button>}
        {bug && <div className="rounded-md border border-major/50 p-4">
          <p className="font-semibold text-major">Repeated error: a bug report goes to the model development team.</p>
          {!bug.released ? <button className="btn mt-3" onClick={() => { log.release('Fix of the product HS check'); setBug({ released: true }) }}>Development team: release a fix</button>
            : <button className="btn-primary mt-3" onClick={() => { setBug(null); doRerun() }}><Refresh />Run again with version {log.version()}</button>}
        </div>}
        {msg && <p className="mt-3 inline-flex items-center gap-2 text-sm text-ok" role="status"><Check />{msg}</p>}
      </Section>

      <Section title="Technical overview">
        <dl className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div><dt className="label">Model</dt><dd>Prototype transcription v{rec?.adapter?.adapter_version?.split(' ')[0]}</dd></div>
          <div><dt className="label">Rule engine</dt><dd>v{result.engine_version} · rules v{result.rulebase_version}</dd></div>
          <div><dt className="label">Values read</dt><dd className="flex flex-wrap gap-1"><Tag s="stated" /><span className="tabular-nums mr-2">{count('stated')}</span><Tag s="inferred" /><span className="tabular-nums mr-2">{count('inferred')}</span><Tag s="missing" /><span className="tabular-nums mr-2">{count('missing')}</span><Tag s="unreadable" /><span className="tabular-nums">{count('unreadable')}</span></dd></div>
          <div><dt className="label">Processing</dt><dd>{errors.length ? <span className="text-crit">{errors.length} error(s)</span> : <span className="text-ok">No errors</span>}
            {conflicts > 0 && <span className="block">{conflicts} line(s) with documents that do not agree</span>}
            {unmatched.length > 0 && <span className="block">{unmatched.length} document(s) not linked</span>}</dd></div>
        </dl>
        {errors.length > 0 && <ul className="mt-3 text-sm text-crit list-disc pl-5">{errors.slice(-3).map((e, i) => <li key={i}>{e.detail}</li>)}</ul>}
      </Section>
      <Findings result={result} onRule={onRule} />
      <TolerancePanel result={result} />
      <Section title="Requirement by requirement"><Requirements result={result} onRule={onRule} /></Section>
      <InfoRequest result={result} title="Draft request to the SME" />
    </div>
  )
}
