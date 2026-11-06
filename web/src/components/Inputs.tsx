import { useMemo, useState } from 'react'
import { RULE_DATA_SHORT, Section, Tag } from './ui'
import { imageUrl } from '../lib/data'
import { Upload as UploadIcon } from './icons'

const DOC_NAME: Record<string, string> = {
  exporter_profile: 'Exporter profile', bill_of_materials: 'Bill of materials', appendix_iii_a: 'Supplier declaration',
  supplier_invoice: 'Supplier invoice', production_notes: 'Production notes',
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

const ILL = <span className="rounded bg-major/15 px-1 text-major">illegible</span>
const isNum = (c: string) => /^\d[\d,]*\.\d+$/.test(c)
const isAmount = (v: string) => /^([\d.,]+|\[illegible\])\s?(GHS|EUR|GH₵|Ghc)$/.test(v.trim())

function Paper({ text }: { text: string }) {
  const lines = text.split('\n')
  const blocks: any[] = []
  const push = (t: string, v: any) => {
    const last = blocks[blocks.length - 1]
    if (last && last.t === t && t !== 'p' && t !== 'h') last.rows.push(v)
    else blocks.push({ t, rows: [v] })
  }
  lines.forEach((l, i) => {
    const s = l.trim()
    if (!s) return
    if (s.includes(' | ')) return push('table', s.split('|').map(c => c.trim()))
    if (i === 0 || (/^[A-ZÀ-Ý ()’'–,\-]+$/.test(s) && s.length > 3)) return blocks.push({ t: 'h', v: s, first: i === 0 })
    const m = s.match(/^([^:]{2,40}?)\s?:\s(.*)$/)
    if (m && s.length < 160) return push(isAmount(m[2]) ? 'kvm' : 'kv', [m[1], m[2]])
    blocks.push({ t: 'p', v: s })
  })
  return (
    <div className="paper rounded-md border border-line p-5 sm:p-7 text-sm">
      {blocks.map((b, i) => {
        if (b.t === 'h') return <p key={i} className={b.first ? 'text-base font-semibold tracking-wide mb-4 pb-3 border-b border-line' : 'font-semibold tracking-wide mt-5 mb-2'}>{b.v}</p>
        if (b.t === 'kv' || b.t === 'kvm') {
          const money = b.t === 'kvm'
          return <dl key={i} className={`grid ${money ? 'grid-cols-[minmax(0,1fr)_max-content]' : 'grid-cols-[max-content_minmax(0,1fr)]'} gap-x-8 gap-y-1 my-2 ${money ? 'max-w-md' : ''}`}>
            {b.rows.map(([k, v]: string[], j: number) => <div key={j} className="contents">
              <dt className="text-muted">{k}</dt>
              <dd className={money ? 'text-right tabular-nums' : ''}>{v.includes('[illegible]') ? ILL : v}</dd></div>)}
          </dl>
        }
        if (b.t === 'table') {
          const [head, ...body] = b.rows
          return <div key={i} className="overflow-x-auto my-3"><table className="data text-xs">
            <thead><tr>{head.map((h: string, k: number) => <th key={k} className={body.length && body.every((r: string[]) => isNum(r[k] ?? '') || r[k] === '[illegible]') ? 'num' : ''}>{h}</th>)}</tr></thead>
            <tbody>{body.map((r: string[], k: number) => <tr key={k}>{r.map((c, j) => <td key={j} className={isNum(c) ? 'num' : ''}>{c === '[illegible]' ? ILL : c}</td>)}</tr>)}</tbody>
          </table></div>
        }
        return <p key={i} className="mt-4 pt-3 border-t border-line italic">{b.v}</p>
      })}
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
      <p className="text-sm max-w-3xl">The model reads each document, whether it is typed, handwritten or multilingual, and puts every value into a fixed field together with the text it comes from.
        Each value gets a tag: <b>stated</b> when it is written in a document, <b>inferred</b> when it is derived, or <b>missing</b> or <b>unreadable</b>. Missing values are never guessed.
        The model then identifies the HS codes and then finds the rule for the declared HS heading.</p>
      <div className="flex flex-wrap gap-2 my-4" role="group" aria-label="Filter by tag">
        {TAGS.map(t => (
          <button key={t} aria-pressed={show.includes(t)} onClick={() => setShow(s => s.includes(t) ? s.filter(x => x !== t) : [...s, t])}
            className={`chip !text-sm !px-2.5 !py-1 ${show.includes(t) ? 'bg-accent-soft border-accent text-accent' : 'border-line text-muted'}`}>
            {t} <span className="tabular-nums font-semibold">{count[t]}</span></button>))}
      </div>
      <div className="overflow-x-auto max-h-[28rem] overflow-y-auto"><table className="data">
        <thead><tr><th>Field</th><th>Value in the document</th><th>Tag</th><th>Document</th></tr></thead>
        <tbody>{rows.map((t: any, i: number) => (
          <tr key={i}><td className="min-w-[200px]">{t.label ?? t.field}</td>
            <td className="min-w-[200px]">{String(t.snippet).includes('[illegible]') ? ILL : <span className="font-medium">{t.snippet}</span>}</td>
            <td><Tag s={t.status} /></td><td className="whitespace-nowrap text-muted">{docName(rec, t.doc_id)}</td></tr>))}</tbody>
      </table></div>
    </Section>
  )
}

const ORIGINS = ['ghana', 'state_party', 'non_state_party', 'unknown']
const ORIGIN_TEXT: Record<string, string> = { ghana: 'Ghana', state_party: 'Other AfCFTA country', non_state_party: 'Outside AfCFTA', unknown: 'Unknown' }
const STATUSES = ['stated', 'inferred', 'missing', 'unreadable']
const PROOF: Record<string, string> = { appendix_iii_a: 'Supplier declaration', origin_declaration: 'Origin declaration', supplier_invoice: 'Invoice only' }

const blankInput = (n: number) => ({ id: `M${n}`, description: '', hs_code: null, hs_field: { status: 'missing' }, origin_class: 'unknown', supplier_country: null,
  customs_value: { amount: null, currency: 'GHS', status: 'missing' }, fob_value: { amount: null, currency: 'GHS', status: 'missing' },
  declaration: { type: null, present: false }, food_aid: null, conflicts: [], quantity: { value: null, unit: 'kg' } })
const blankStep = (n: number) => ({ id: `S${n}`, description: '', operation_code: 'unspecified_processing', location_country: 'Ghana', status: 'stated' })

/** Empty record for manual entry (no prepared case behind it). */
export const MANUAL_CASE = () => ({
  case_id: 'manual', synthetic: true, exporter: { name: '', registration_no: '' }, consignee: { name: '', country: null }, destination_country: null,
  product: { description: '', declared_hs: '' }, ex_works_price: { amount: null, currency: 'GHS', status: 'missing' },
  inputs: [blankInput(1)], production_steps: [blankStep(1)], packaging: [], invoice: {},
})

export function ModelTab({ rec, extracted, setExtracted, canRun, onRun, rules, editing, setEditing, manual }: {
  rec: any; extracted: any; setExtracted: (c: any) => void; canRun: boolean; onRun: () => void; rules: any; editing: boolean; setEditing: (b: boolean) => void; manual?: boolean }) {
  const upd = (fn: (c: any) => void) => { const c = structuredClone(extracted); fn(c); setExtracted(c) }
  const opmap: Record<string, any> = Object.fromEntries((rules?.operation_map ?? []).map((m: any) => [m.code, m]))
  const stepType = (code: string) => {
    const m = opmap[code]
    if (!m) return ['Unclear', 'text-major']
    if (m.status === 'listed') return ['Not eligible on its own under AfCFTA guidelines', 'text-muted']
    if (m.status === 'not_listed') return ['Accepted production in the AfCFTA', 'text-ok']
    return ['Unclear', 'text-major']
  }
  const inp = 'rounded border border-line bg-bg px-1.5 py-0.5 text-sm'
  const money = (v: any) => v == null ? '—' : Number(v).toLocaleString('en', { minimumFractionDigits: 2 })
  const setMoney = (v: string) => ({ amount: v.replace(/,/g, '') || null, currency: 'GHS', status: v ? 'stated' : 'missing' })
  const del = (fn: () => void) => <button className="text-xs text-muted hover:text-crit" onClick={fn} aria-label="Remove">Remove</button>
  return (
    <Section kicker="Stage 3 · Model" title={manual ? 'Manual entry' : 'Extracted data'}
      right={<div className="flex gap-2">{!manual && <button className="btn" aria-pressed={editing} onClick={() => setEditing(!editing)}>{editing ? 'Stop editing' : 'Edit the data'}</button>}
        <button className="btn-primary" disabled={!canRun} onClick={onRun}>Run the check</button></div>}>
      <p className="note mb-4">Model: <b className="text-ink">Tessera Prototype</b> · Rule data: {RULE_DATA_SHORT}</p>
      {manual && <p className="text-sm mb-4 max-w-3xl">Type the data from your records. Fields you leave empty count as missing; the check never assumes a value.{!canRun && ' The check is still loading in your browser.'}</p>}
      <h3 className="h3 mb-2">Product</h3>
      <div className="grid sm:grid-cols-3 gap-3 text-sm mb-6">
        <div className="sm:col-span-3"><p className="label">Description</p>{editing ? <input className={`${inp} w-full`} placeholder="e.g. Instant millet porridge mix, 500 g pouches" value={extracted.product?.description ?? ''} onChange={e => upd(c => { c.product.description = e.target.value })} /> : <p>{extracted.product?.description ?? '—'}</p>}</div>
        <div><p className="label">HS code</p>{editing ? <input className={inp} placeholder="1901.90" value={extracted.product?.declared_hs ?? ''} onChange={e => upd(c => { c.product.declared_hs = e.target.value })} /> : <p>{extracted.product?.declared_hs ?? '—'}</p>}</div>
        <div><p className="label">Ex-works price (GHS)</p>{editing ? <input className={inp} inputMode="decimal" value={extracted.ex_works_price?.amount ?? ''} onChange={e => upd(c => { c.ex_works_price = setMoney(e.target.value) })} />
          : <p>GHS {money(extracted.ex_works_price?.amount)} <Tag s={extracted.ex_works_price?.status ?? 'missing'} /></p>}</div>
        {manual ? <div><p className="label">Destination country</p><input className={inp} placeholder="e.g. Nigeria" value={extracted.destination_country ?? ''} onChange={e => upd(c => { c.destination_country = e.target.value || null; c.consignee = { ...c.consignee, country: e.target.value || null } })} /></div>
          : <div><p className="label">HS code in doubt</p>{editing ? <input type="checkbox" checked={!!extracted.product?.hs_doubt} onChange={e => upd(c => { c.product.hs_doubt = e.target.checked })} />
          : <p>{extracted.product?.hs_doubt ? `Yes – ${extracted.product.hs_doubt_reason}` : 'No'}</p>}</div>}
      </div>
      <h3 className="h3 mb-2">Ingredients</h3>
      <div className="overflow-x-auto mb-2"><table className="data">
        <thead><tr><th>Ingredient</th><th>HS code</th><th>Origin</th><th>Country</th><th className="num">Value (GHS)</th><th>Proof of origin</th><th>Food aid</th>{editing && <th />}</tr></thead>
        <tbody>{(extracted.inputs || []).map((x: any, i: number) => (
          <tr key={x.id + i}>
            <td>{editing ? <input className={inp} placeholder="Ingredient" value={x.description} onChange={e => upd(c => { c.inputs[i].description = e.target.value })} /> : x.description}
              {x.conflicts?.length > 0 && <span className="block text-xs text-major">Contradictory information: {x.conflicts.map((k: any) => k.field.replace('_', ' ')).join(', ')}</span>}</td>
            <td className="whitespace-nowrap">{editing ? <input className={`${inp} w-24`} placeholder="1101.00" value={x.hs_code ?? ''} onChange={e => upd(c => { c.inputs[i].hs_code = e.target.value || null; c.inputs[i].hs_field = { status: e.target.value ? 'stated' : 'missing' }; c.inputs[i].hs_doubt = false })} />
              : <>{x.hs_code ?? '—'}{x.hs_doubt && <span className="block text-xs text-major">Does not fit the description</span>}</>}</td>
            <td>{editing ? <select className={inp} value={x.origin_class} onChange={e => upd(c => { c.inputs[i].origin_class = e.target.value })}>{ORIGINS.map(o => <option key={o} value={o}>{ORIGIN_TEXT[o]}</option>)}</select> : ORIGIN_TEXT[x.origin_class]}</td>
            <td>{editing ? <input className={`${inp} w-28`} value={x.supplier_country ?? ''} onChange={e => upd(c => { c.inputs[i].supplier_country = e.target.value || null })} /> : x.supplier_country ?? '—'}</td>
            <td className="num">{editing ? <span className="inline-flex gap-1"><input className={`${inp} w-24 text-right`} inputMode="decimal" value={x.customs_value?.amount ?? ''} onChange={e => upd(c => { const m = setMoney(e.target.value); c.inputs[i].customs_value = m; c.inputs[i].fob_value = m })} />
              {!manual && <select className={inp} value={x.customs_value?.status} onChange={e => upd(c => { c.inputs[i].customs_value.status = e.target.value })}>{STATUSES.map(s => <option key={s}>{s}</option>)}</select>}</span>
              : <span className="whitespace-nowrap">{money(x.customs_value?.amount)}{x.customs_value?.currency && x.customs_value.currency !== 'GHS' ? ` ${x.customs_value.currency}` : ''} <Tag s={x.customs_value?.status ?? 'missing'} /></span>}</td>
            <td>{editing ? <label className="inline-flex items-center gap-1.5 text-sm"><input type="checkbox" checked={!!x.declaration?.present} onChange={e => upd(c => { c.inputs[i].declaration = { type: e.target.checked ? 'appendix_iii_a' : null, present: e.target.checked } })} />Supplier declaration</label>
              : x.declaration?.present ? PROOF[x.declaration.type] ?? x.declaration.type : 'None'}</td>
            <td>{editing ? <select className={inp} value={String(x.food_aid)} onChange={e => upd(c => { c.inputs[i].food_aid = e.target.value === 'null' ? null : e.target.value === 'true' })}><option value="false">No</option><option value="true">Yes</option><option value="null">Unknown</option></select>
              : x.food_aid === null ? 'Unknown' : x.food_aid ? 'Yes' : 'No'}</td>
            {editing && <td>{del(() => upd(c => { c.inputs.splice(i, 1) }))}</td>}
          </tr>))}</tbody>
      </table></div>
      {editing && <button className="btn mb-4" onClick={() => upd(c => { c.inputs.push(blankInput(c.inputs.length + 1)) })}>Add an ingredient</button>}
      <h3 className="h3 mt-6 mb-2">Production steps</h3>
      <div className="overflow-x-auto"><table className="data">
        <thead><tr><th>Step</th><th>Description</th><th>Location</th><th>Type of operation</th>{editing && <th />}</tr></thead>
        <tbody>{(extracted.production_steps || []).map((s: any, i: number) => {
          const [txt, cls] = stepType(s.operation_code)
          return <tr key={s.id + i}><td>{i + 1}</td>
            <td>{editing ? <input className={`${inp} w-full min-w-[220px]`} placeholder="e.g. Cooking by extrusion" value={s.description} onChange={e => upd(c => { c.production_steps[i].description = e.target.value })} /> : s.description}</td>
            <td>{editing ? <input className={`${inp} w-28`} value={s.location_country ?? ''} onChange={e => upd(c => { c.production_steps[i].location_country = e.target.value || null })} /> : s.location_country ?? '—'}</td>
            <td>{editing ? <select className={inp} value={s.operation_code} onChange={e => upd(c => { c.production_steps[i].operation_code = e.target.value })}>
              {(rules?.operation_map ?? []).map((m: any) => <option key={m.code} value={m.code}>{m.label}</option>)}</select>
              : <span className={cls}>{txt}</span>}</td>
            {editing && <td>{del(() => upd(c => { c.production_steps.splice(i, 1) }))}</td>}</tr>
        })}</tbody>
      </table></div>
      {editing && <button className="btn mt-2" onClick={() => upd(c => { c.production_steps.push(blankStep(c.production_steps.length + 1)) })}>Add a step</button>}
    </Section>
  )
}
