import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getCase, getIndex } from '../lib/data'
import { PageHead, STAGES } from '../components/ui'

const base = import.meta.env.BASE_URL
const text = (p: string) => fetch(base + p).then(r => r.text())
const J = (o: any) => JSON.stringify(o, null, 1)

function Pane({ title, children }: { title: string; children: string }) {
  return <div className="min-w-0"><p className="label mb-1">{title}</p>
    <pre className="pre max-h-80 overflow-auto">{children}</pre></div>
}

export default function Logic() {
  const { caseId = 'T3c' } = useParams()
  const nav = useNavigate()
  const [idx, setIdx] = useState<any>(null), [rec, setRec] = useState<any>(null)
  const [prompt, setPrompt] = useState(''), [engineSrc, setEngineSrc] = useState(''), [stubSrc, setStubSrc] = useState('')
  useEffect(() => { getIndex().then(setIdx); text('data/prompts/extract_v1.txt').then(setPrompt); text('py/engine/assess.py').then(setEngineSrc); text('data/stub_excerpt.txt').then(setStubSrc).catch(() => {}) }, [])
  useEffect(() => { getCase(caseId).then(setRec) }, [caseId])
  if (!rec) return <p className="p-8 text-muted">Loading…</p>
  const tol = engineSrc.slice(engineSrc.indexOf('    lhs, rhs'), engineSrc.indexOf('    if not quiet:\n        ctx.log("tolerance"'))
  const stages = [
    { code: `Generator ${rec.meta.generator_version}, seed ${rec.meta.seed}\nspec = ${J(rec.meta.spec)}`, input: `Injected defects: ${rec.meta.defects.join(', ') || 'none'}`,
      output: rec.documents.map((d: any) => `[${d.doc_id}] ${d.type} · ${d.language} · ${d.format}`).join('\n') },
    { code: `PROMPT (live provider, adapter/prompts/extract_v1.txt)\n\n${prompt}`, input: rec.documents.map((d: any) => `[${d.doc_id}]\n${d.text}`).join('\n\n'),
      output: rec.adapter.field_tags.map((t: any) => `${t.field}: ${t.status} ← "${t.snippet}" (${t.doc_id})`).join('\n') },
    { code: `Prototype transcription v${rec.adapter.adapter_version?.split(' ')[0]} (adapter/stub.py)\n\n${stubSrc}`,
      input: 'documents (text layer)', output: J(rec.extracted) },
    { code: `engine/assess.py (the same file runs in the browser). Exact test of the 15% limit:\n\n${tol}`, input: J(rec.extracted).slice(0, 4000) + '\n…',
      output: `${rec.result.trace.map((t: any) => `[${t.step}] ${t.detail}`).join('\n')}\n\nOUTCOME: ${J(rec.result.outcome)}\n\nFINDINGS:\n${rec.result.findings.map((f: any) => `${f.id} ${f.severity}: ${f.title} [${f.rule_ids.join(', ')}]`).join('\n')}` },
    { code: 'Service blueprint:\n1. Is the citation sufficient? No: ask the SME for clarification.\n2. Is the HS code correct? No: the adviser enters the code and the case runs again. The same error two times: bug report to the development team.\n3. Type of result. Missing data: request to the SME. Data does not agree: clarification request. Likely / likely not: approve and send.',
      input: `Outcome: ${rec.result.outcome.label}`, output: rec.result.missing_info_request || 'No request needed – adviser approves and sends.' },
    { code: 'Stage 6: the log records each correction, new run, bug report and error. The export contains counts only.\nRepeated-error limit: 2 (rules.json).',
      input: 'Event log', output: `Answer-key comparison for this case:\n${J(rec.comparison)}\n\nTranscription vs ground truth:\n${J(rec.transcription)}` },
  ]
  return (
    <>
      <PageHead title="Show the logic">Code or prompt, input and output for each stage of the selected case.</PageHead>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 space-y-6">
        <label className="card p-4 flex items-center gap-3 text-sm"><span className="label">Case</span>
          <select className="field" value={caseId} onChange={e => nav(`/logic/${e.target.value}`)}>
            {idx?.cases.map((c: any) => <option key={c.case_id}>{c.case_id}</option>)}</select>
          <span className="note">{rec.meta.spec.scenario ?? rec.meta.defects.join(', ')}</span></label>
        {STAGES.slice(0, 4).map(([n, t, d], i) => (
          <section key={n} className="card p-5">
            <p className="label">Stage {n}</p><h2 className="h2">{t}</h2><p className="note mb-3">{d}</p>
            <div className="grid lg:grid-cols-3 gap-3"><Pane title="Code / prompt">{stages[i].code}</Pane><Pane title="Input">{stages[i].input}</Pane><Pane title="Output">{stages[i].output}</Pane></div>
          </section>))}
      </div>
    </>
  )
}
