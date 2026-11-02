import { useMemo, useState } from 'react'
import { Section, Tag } from './ui'
import { imageUrl } from '../lib/data'
import { Upload as UploadIcon } from './icons'

const DOC_NAME: Record<string, string> = {
  exporter_profile: 'Exporter profile', bill_of_materials: 'Bill of materials', appendix_iii_a: 'Supplier declaration',
  certificate_of_origin: 'Certificate of origin', supplier_invoice: 'Supplier invoice', production_notes: 'Production notes',
  costing_sheet: 'Costing sheet', export_invoice: 'Export invoice',
}
export const docName = (rec: any, id: string) => {
  const d = rec?.documents?.find((x: any) => x.doc_id === id)
  return d ? `${DOC_NAME[d.type] ?? d.type}${d.input_id ? ` (${d.input_id})` : ''}` : id
}

export function Upload({ onSample, onManual }: { onSample: () => void; onManual: () => void }) {
  const [file, setFile] = useState<{ name: string; url: string; type: string } | null>(null)
  const [drag, setDrag] = useState(false)
  const take = (f?: File) => { if (f) setFile({ name: f.name, url: URL.createObjectURL(f), type: f.type }) }
  return (
    <Section title="Upload documents">
      <label onDragOver={e => { e.preventDefault(); setDrag(true) }} onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); take(e.dataTransfer.files?.[0]) }}
        className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-10 text-center cursor-pointer transition-colors ${drag ? 'border-accent bg-accent-soft' : 'border-line hover:border-accent'}`}>
        <UploadIcon size={28} className="text-accent" />
        <span className="font-medium">Drop a file here or select a file</span>
        <span className="note">Bill of materials, supplier declaration, invoice, costing sheet or a photo of handwritten records</span>
        <input type="file" accept="image/*,.pdf,.txt" className="sr-only" onChange={e => take(e.target.files?.[0])} />
      </label>
      {file && <div className="mt-4 text-sm space-y-3">
        {file.type.startsWith('image/') && <img src={file.url} alt={`Preview of ${file.name}`} className="max-h-56 rounded-md border border-line" />}
        <p><b>{file.name}</b> is loaded. This prototype cannot read new files. Type the data in manual entry, or open a prepared case.</p>
      </div>}
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn" onClick={onManual}>Manual entry</button>
        <button className="btn" onClick={onSample}>Open a prepared case</button>
      </div>
    </Section>
  )
}

function Paper({ text }: { text: string }) {
  const lines = text.split('\n')
  const blocks: any[] = []
  let table: string[][] | null = null
  const flush = () => { if (table) { blocks.push({ t: 'table', rows: table }); table = null } }
  lines.forEach((l, i) => {
    if (i === 0 && /SYNTH/.test(l)) return
    if (l.includes(' | ')) { (table ??= []).push(l.split('|').map(c => c.trim())); return }
    flush()
    if (i === 1 || /^[A-ZÀ-Ý ()’'–,\-]+$/.test(l.trim()) && l.trim().length > 3) blocks.push({ t: 'h', v: l })
    else if (/^\s+\S+.*:/.test(l)) blocks.push({ t: 'sub', v: l.trim() })
    else if (/^\d+\./.test(l)) blocks.push({ t: 'step', v: l })
    else if (/^[^:]{2,40}\s?:\s/.test(l)) { const [k, ...v] = l.split(/\s?:\s/); blocks.push({ t: 'kv', k, v: v.join(': ') }) }
    else if (l.trim()) blocks.push({ t: 'p', v: l })
  })
  flush()
  return (
    <div className="paper watermark rounded-md border border-line p-5 sm:p-6 text-sm">
      <p className="text-[10px] uppercase tracking-widest text-muted mb-3">{lines[0]}</p>
      {blocks.map((b, i) => b.t === 'h' ? <p key={i} className="font-semibold tracking-wide mt-3 first:mt-0 mb-2">{b.v}</p>
        : b.t === 'kv' ? <div key={i} className="grid grid-cols-[minmax(110px,auto)_1fr] gap-3 py-0.5"><span className="text-muted">{b.k}</span><span>{b.v.includes('[illegible]') ? <span className="rounded bg-major/15 px-1 text-major">illegible</span> : b.v}</span></div>
        : b.t === 'step' ? <p key={i} className="mt-2">{b.v}</p>
        : b.t === 'sub' ? <p key={i} className="ml-5 note">{b.v}</p>
        : b.t === 'table' ? <div key={i} className="overflow-x-auto my-2"><table className="data text-xs">
            <thead><tr>{b.rows[0][0] === 'ID' ? b.rows[0].map((h: string, k: number) => <th key={k}>{h}</th>) : null}</tr></thead>
            <tbody>{(b.rows[0][0] === 'ID' ? b.rows.slice(1) : b.rows).map((r: string[], k: number) => <tr key={k}>{r.map((c, j) => <td key={j} className={/^[\d.,]+$/.test(c) ? 'num' : ''}>{c === '[illegible]' ? <span className="rounded bg-major/15 px-1 text-major">illegible</span> : c}</td>)}</tr>)}</tbody>
          </table></div>
        : <p key={i} className="mt-2">{b.v}</p>)}
    </div>
  )
}

export function Documents({ rec }: { rec: any }) {
  const [open, setOpen] = useState<string>(rec.documents[0]?.doc_id)
  const d = rec.documents.find((x: any) => x.doc_id === open) ?? rec.documents[0]
  return (
    <Section kicker="Stage 1 · Inputs and data" title="Documents from the SME">
      <div className="grid md:grid-cols-[220px_1fr] gap-5">
        <div className="flex md:flex-col gap-1.5 overflow-x-auto" role="tablist" aria-label="Documents">
          {rec.documents.map((x: any) => (
            <button key={x.doc_id} role="tab" aria-selected={open === x.doc_id} onClick={() => setOpen(x.doc_id)}
              className={`shrink-0 text-left rounded-md px-3 py-2 text-sm border transition-colors ${open === x.doc_id ? 'bg-accent-soft text-accent border-accent' : 'border-line hover:border-accent'}`}>
              {docName(rec, x.doc_id)}
              <span className="block text-xs text-muted">{x.language === 'fr' ? 'French' : 'English'} · {x.format === 'handwritten' ? 'handwritten' : 'typed'}</span>
            </button>))}
        </div>
        <div className="min-w-0">
          {d.format === 'handwritten' && <img src={imageUrl(rec.case_id, d.doc_id)} alt={`Handwritten ${docName(rec, d.doc_id)}`}
            className="w-full rounded-md border border-line mb-3" loading="lazy" />}
          {d.format === 'handwritten'
            ? <details><summary className="note cursor-pointer mb-2">Typed text behind the image</summary><Paper text={d.text} /></details>
            : <Paper text={d.text} />}
        </div>
      </div>
    </Section>
  )
}

const TAGS = ['stated', 'inferred', 'missing', 'unreadable'] as const
export function AiTask({ rec }: { rec: any }) {
  const tags = rec?.adapter?.field_tags || []
  const [show, setShow] = useState<string[]>([...TAGS])
  const count = useMemo(() => Object.fromEntries(TAGS.map(t => [t, tags.filter((x: any) => x.status === t).length])), [tags])
  const rows = tags.filter((t: any) => show.includes(t.status))
  return (
    <Section kicker="Stage 2 · AI task" title="Read, extract and check">
      <p className="text-sm max-w-3xl">The model reads each document, whether it is typed, handwritten or in French, and puts every value into a fixed field together with the text it comes from.
        Each value gets a tag: <b>stated</b> when it is written in a document, <b>inferred</b> when it is derived, or <b>missing</b> or <b>unreadable</b>. Missing values are never guessed.
        The model then checks that the HS codes agree with the descriptions and finds the rule for the declared HS heading.</p>
      <div className="flex flex-wrap gap-2 my-4" role="group" aria-label="Filter by tag">
        {TAGS.map(t => (
          <button key={t} aria-pressed={show.includes(t)} onClick={() => setShow(s => s.includes(t) ? s.filter(x => x !== t) : [...s, t])}
            className={`chip !text-sm !px-2.5 !py-1 ${show.includes(t) ? 'bg-accent-soft border-accent text-accent' : 'border-line text-muted'}`}>
            {t} <span className="tabular-nums font-semibold">{count[t]}</span></button>))}
      </div>
      <div className="overflow-x-auto max-h-[28rem] overflow-y-auto"><table className="data">
        <thead><tr><th>Field</th><th>Tag</th><th>Text in the document</th><th>Document</th></tr></thead>
        <tbody>{rows.map((t: any, i: number) => (
          <tr key={i}><td className="whitespace-nowrap">{t.field}</td><td><Tag s={t.status} /></td>
            <td className="text-muted">{t.snippet}</td><td className="whitespace-nowrap">{docName(rec, t.doc_id)}</td></tr>))}</tbody>
      </table></div>
    </Section>
  )
}

const ORIGINS = ['ghana', 'state_party', 'non_state_party', 'unknown']
const ORIGIN_TEXT: Record<string, string> = { ghana: 'Ghana', state_party: 'Other AfCFTA country', non_state_party: 'Outside AfCFTA', unknown: 'Unknown' }
const STATUSES = ['stated', 'inferred', 'missing', 'unreadable']
const PROOF: Record<string, string> = { appendix_iii_a: 'Supplier declaration', certificate_of_origin: 'Certificate of origin', origin_declaration: 'Origin declaration', supplier_invoice: 'Invoice only' }

export function ModelTab({ rec, extracted, setExtracted, canRun, onRun, rules, editing, setEditing }: {
  rec: any; extracted: any; setExtracted: (c: any) => void; canRun: boolean; onRun: () => void; rules: any; editing: boolean; setEditing: (b: boolean) => void }) {
  const upd = (fn: (c: any) => void) => { const c = structuredClone(extracted); fn(c); setExtracted(c) }
  const opmap: Record<string, any> = Object.fromEntries((rules?.operation_map ?? []).map((m: any) => [m.code, m]))
  const stepType = (code: string) => {
    const m = opmap[code]
    if (!m) return ['Unclear', 'text-major']
    if (m.status === 'listed') return [`Simple operation – Art. 7(1)(${m.art7_letter})`, 'text-muted']
    if (m.status === 'not_listed') return ['More than a simple operation', 'text-ok']
    return ['Unclear', 'text-major']
  }
  const inp = 'rounded border border-line bg-bg px-1.5 py-0.5 text-sm'
  const money = (v: any) => v == null ? '—' : Number(v).toLocaleString('en', { minimumFractionDigits: 2 })
  return (
    <Section kicker="Stage 3 · Model" title="Extracted data"
      right={<div className="flex gap-2"><button className="btn" aria-pressed={editing} onClick={() => setEditing(!editing)}>{editing ? 'Stop editing' : 'Manual entry'}</button>
        <button className="btn-primary" disabled={!canRun} onClick={onRun}>Run the check</button></div>}>
      <p className="note mb-4">Model: <b className="text-ink">Prototype transcription v{rec?.adapter?.adapter_version?.split(' ')[0] ?? '–'}</b></p>
      <h3 className="h3 mb-2">Product</h3>
      <div className="grid sm:grid-cols-3 gap-3 text-sm mb-6">
        <div><p className="label">HS code</p>{editing ? <input className={inp} value={extracted.product?.declared_hs ?? ''} onChange={e => upd(c => { c.product.declared_hs = e.target.value })} /> : <p>{extracted.product?.declared_hs ?? '—'}</p>}</div>
        <div><p className="label">Ex-works price</p>{editing ? <input className={inp} inputMode="decimal" value={extracted.ex_works_price?.amount ?? ''}
          onChange={e => upd(c => { c.ex_works_price = { amount: e.target.value || null, currency: 'GHS', status: e.target.value ? 'stated' : 'missing' } })} />
          : <p>GHS {money(extracted.ex_works_price?.amount)} <Tag s={extracted.ex_works_price?.status ?? 'missing'} /></p>}</div>
        <div><p className="label">HS code in doubt</p>{editing ? <input type="checkbox" checked={!!extracted.product?.hs_doubt} onChange={e => upd(c => { c.product.hs_doubt = e.target.checked })} />
          : <p>{extracted.product?.hs_doubt ? `Yes – ${extracted.product.hs_doubt_reason}` : 'No'}</p>}</div>
        <div className="sm:col-span-3"><p className="label">Description</p><p>{extracted.product?.description ?? '—'}</p></div>
      </div>
      <h3 className="h3 mb-2">Ingredients</h3>
      <div className="overflow-x-auto mb-2"><table className="data">
        <thead><tr><th>Line</th><th>Ingredient</th><th>HS code</th><th>Origin</th><th>Country</th><th className="num">Value (GHS)</th><th>Proof of origin</th><th>Food aid</th></tr></thead>
        <tbody>{(extracted.inputs || []).map((x: any, i: number) => (
          <tr key={x.id + i}>
            <td>{x.id}</td>
            <td>{editing ? <input className={inp} value={x.description} onChange={e => upd(c => { c.inputs[i].description = e.target.value })} /> : x.description}
              {x.conflicts?.length > 0 && <span className="block text-xs text-major">Documents do not agree: {x.conflicts.map((k: any) => k.field.replace('_', ' ')).join(', ')}</span>}</td>
            <td className="whitespace-nowrap">{editing ? <input className={`${inp} w-24`} value={x.hs_code ?? ''} onChange={e => upd(c => { c.inputs[i].hs_code = e.target.value || null; c.inputs[i].hs_field = { status: e.target.value ? 'stated' : 'missing' }; c.inputs[i].hs_doubt = false })} />
              : <>{x.hs_code ?? '—'}{x.hs_doubt && <span className="block text-xs text-major">Does not fit the description</span>}</>}</td>
            <td>{editing ? <select className={inp} value={x.origin_class} onChange={e => upd(c => { c.inputs[i].origin_class = e.target.value })}>{ORIGINS.map(o => <option key={o} value={o}>{ORIGIN_TEXT[o]}</option>)}</select> : ORIGIN_TEXT[x.origin_class]}</td>
            <td>{editing ? <input className={`${inp} w-28`} value={x.supplier_country ?? ''} onChange={e => upd(c => { c.inputs[i].supplier_country = e.target.value || null })} /> : x.supplier_country ?? '—'}</td>
            <td className="num">{editing ? <span className="inline-flex gap-1"><input className={`${inp} w-24 text-right`} value={x.customs_value?.amount ?? ''} onChange={e => upd(c => { c.inputs[i].customs_value = { ...c.inputs[i].customs_value, amount: e.target.value || null } })} />
              <select className={inp} value={x.customs_value?.status} onChange={e => upd(c => { c.inputs[i].customs_value.status = e.target.value })}>{STATUSES.map(s => <option key={s}>{s}</option>)}</select></span>
              : <span className="whitespace-nowrap">{money(x.customs_value?.amount)}{x.customs_value?.currency && x.customs_value.currency !== 'GHS' ? ` ${x.customs_value.currency}` : ''} <Tag s={x.customs_value?.status ?? 'missing'} /></span>}</td>
            <td>{editing ? <input type="checkbox" checked={!!x.declaration?.present} onChange={e => upd(c => { c.inputs[i].declaration = { type: e.target.checked ? (c.inputs[i].origin_class === 'ghana' ? 'appendix_iii_a' : 'certificate_of_origin') : null, present: e.target.checked } })} />
              : x.declaration?.present ? PROOF[x.declaration.type] ?? x.declaration.type : 'None'}</td>
            <td>{editing ? <select className={inp} value={String(x.food_aid)} onChange={e => upd(c => { c.inputs[i].food_aid = e.target.value === 'null' ? null : e.target.value === 'true' })}><option value="false">No</option><option value="true">Yes</option><option value="null">Unknown</option></select>
              : x.food_aid === null ? 'Unknown' : x.food_aid ? 'Yes' : 'No'}</td>
          </tr>))}</tbody>
      </table></div>
      {editing && <button className="btn mb-4" onClick={() => upd(c => { c.inputs.push({ id: `M${c.inputs.length + 1}`, description: 'New ingredient', hs_code: null, hs_field: { status: 'missing' }, origin_class: 'unknown', supplier_country: null, customs_value: { amount: null, currency: 'GHS', status: 'missing' }, fob_value: { amount: null, currency: 'GHS', status: 'missing' }, declaration: { type: null, present: false }, food_aid: null, conflicts: [], quantity: { value: null, unit: 'kg' } }) })}>Add an ingredient</button>}
      <h3 className="h3 mt-6 mb-2">Production steps</h3>
      <div className="overflow-x-auto"><table className="data">
        <thead><tr><th>Step</th><th>Description</th><th>Location</th><th>Type of operation</th></tr></thead>
        <tbody>{(extracted.production_steps || []).map((s: any, i: number) => {
          const [txt, cls] = stepType(s.operation_code)
          return <tr key={s.id + i}><td>{s.id.replace('S', '')}</td><td>{s.description}</td><td>{s.location_country ?? '—'}</td>
            <td>{editing ? <select className={inp} value={s.operation_code} onChange={e => upd(c => { c.production_steps[i].operation_code = e.target.value })}>
              {(rules?.operation_map ?? []).map((m: any) => <option key={m.code} value={m.code}>{m.label}</option>)}</select>
              : <span className={cls}>{txt}</span>}</td></tr>
        })}</tbody>
      </table></div>
    </Section>
  )
}
