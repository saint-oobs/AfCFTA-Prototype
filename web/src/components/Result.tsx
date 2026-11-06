import { useEffect, useMemo, useRef, useState } from 'react'
import anime from 'animejs'
import { OUTCOME_STYLE, Section, Severity, Status, SEV, SUB } from './ui'
import { reduced, reveal } from '../lib/motion'
import { Copy } from './icons'

const money = (v: any, cur = 'GHS') => v == null ? '—' : `${cur} ${Number(v).toLocaleString('en', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
const pct = (v: any) => v == null ? '—' : `${Number(v).toFixed(1)}%`

export function Stamp({ result, small }: { result: any; small?: boolean }) {
  const o = result.outcome, st = OUTCOME_STYLE[o.label]
  return <div className={`inline-block rounded-md border-[3px] px-4 py-2 ${st.cls}`}>
    <p className={`${small ? 'text-base' : 'text-xl'} font-bold leading-tight flex items-center gap-1.5`}><st.Icon size={small ? 16 : 20} />{o.label}</p>
    {o.sub_reasons.length > 0 && <p className="text-xs font-medium mt-0.5">Reason: {o.sub_reasons.map((s: string) => SUB[s] || s).join('; ')}</p>}
    <p className="text-[11px] opacity-80">Indicative pre-check, not an origin decision</p>
  </div>
}

export function SummaryStrip({ result, extracted, scenario }: { result: any; extracted: any; scenario?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => { reveal(ref.current) }, [result])
  const c = result.components
  return (
    <div ref={ref} className="card p-4 grid md:grid-cols-[auto_1fr] gap-5 items-center" aria-live="polite">
      <Stamp result={result} />
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <div><p className="label">Product</p><p className="text-sm mt-0.5">{extracted?.product?.description?.split('(')[0] ?? '—'}</p><p className="note">HS {extracted?.product?.declared_hs ?? '—'}</p></div>
        <div><p className="label">Heading 19.01 rule</p><div className="mt-1"><Status s={c.tolerance?.status ?? 'not assessed'} /></div></div>
        <div><p className="label">Eligible manufacturing processes</p><div className="mt-1"><Status s={c.article7?.status ?? 'not assessed'} /></div></div>
        {scenario && <p className="col-span-2 lg:col-span-3 note">{scenario.replace(/^[^.]*\(HS [\d.]+\)\.\s*/, '')}</p>}
      </div>
    </div>
  )
}

export function Requirements({ result, onRule, sme }: { result: any; onRule?: (id: string) => void; sme?: boolean }) {
  return (
    <div className="overflow-x-auto"><table className="data">
      <thead><tr><th>Requirement</th><th>What we found</th><th>Result</th>{!sme && <th>Source</th>}</tr></thead>
      <tbody>{result.requirements.map((r: any, i: number) => (
        <tr key={i}><td className="min-w-[180px] font-medium">{r.requirement}</td><td className="min-w-[260px]">{r.evidence}</td>
          <td className="whitespace-nowrap"><Status s={r.status} /></td>
          {!sme && <td className="min-w-[140px]"><button className="text-left text-sm text-accent hover:underline" onClick={() => onRule?.(r.rule_ids[0])}>{r.source}</button></td>}</tr>))}</tbody>
    </table></div>
  )
}

/** SME view: gauge of the share of imported heading 19.01 ingredients, with a plain explanation and an action. */
export function ShareGauge({ result }: { result: any }) {
  const t = result.components.tolerance
  const bar = useRef<HTMLDivElement>(null)
  const share = t?.share_display != null && !t.share_is_lower_bound ? Number(t.share_display) : null
  const scale = Math.max(20, Math.ceil(((share ?? 0) + 3) / 5) * 5)
  useEffect(() => {
    if (!bar.current || share == null) return
    const w = `${(share / scale) * 100}%`
    if (reduced()) bar.current.style.width = w
    else anime({ targets: bar.current, width: ['0%', w], duration: 900, easing: 'easeOutCubic' })
  }, [share, scale])
  if (!t || t.status === 'not assessed') return null
  const headroom = t.headroom != null ? Number(t.headroom) : null
  let text: string, action: string
  if (t.status === 'unclear') {
    text = 'We cannot calculate this share yet, because a value, an HS code or a proof of origin is missing or contradictory.'
    action = 'Send the documents listed under “Information we need from you”.'
  } else if (t.status === 'met') {
    text = 'None of your imported ingredients is a preparation of heading 19.01. This rule is met.'
    action = 'If you add an imported ingredient such as a premix or malt extract, ask us to check again.'
  } else if (t.status === 'not met') {
    text = `Imported ingredients of heading 19.01 are ${pct(share)} of your ex-works price. The limit is 15%.`
    action = `Reduce these ingredients by at least ${money(Math.abs(headroom ?? 0))} per batch, or buy them from Ghana or another AfCFTA country with a proof of origin.`
  } else {
    text = `Imported ingredients of heading 19.01 are ${pct(share)} of your ex-works price. The limit is 15%.`
    action = (headroom ?? 0) <= 0.005 ? 'You are exactly at the limit. Do not increase these ingredients or lower your price without a new check.'
      : `You can use up to ${money(headroom)} more of these ingredients per batch before you reach the limit. Check again if prices or the recipe change.`
  }
  const over = share != null && share > 15
  return (
    <Section title="Imported ingredients of heading 19.01">
      {share != null && <div className="mb-4">
        <div className="relative h-4 rounded-full bg-panel overflow-hidden border border-line" role="img" aria-label={`Share ${pct(share)}, limit 15%`}>
          <div ref={bar} className={`h-full rounded-full ${over ? 'bg-crit' : 'bg-accent'}`} style={{ width: `${(share / scale) * 100}%` }} />
          <div className="absolute top-0 bottom-0 w-0.5 bg-ink" style={{ left: `${(15 / scale) * 100}%` }} />
        </div>
        <div className="relative h-5 text-xs text-muted">
          <span className="absolute" style={{ left: 0 }}>0%</span>
          <span className="absolute -translate-x-1/2 font-semibold text-ink" style={{ left: `${(15 / scale) * 100}%` }}>Limit 15%</span>
          <span className="absolute right-0">{scale}%</span>
        </div>
      </div>}
      <p className="text-sm">{text}</p>
      <p className="text-sm mt-2"><b>What you can do:</b> {action}</p>
    </Section>
  )
}

export function TolerancePanel({ result }: { result: any }) {
  const t = result.components.tolerance
  if (!t || t.status === 'not assessed') return null
  return (
    <Section kicker="Calculation" title="Share of imported heading 19.01 ingredients">
      <div className="overflow-x-auto"><table className="data">
        <thead><tr><th>Imported ingredient of heading 19.01</th><th className="num">Customs value</th></tr></thead>
        <tbody>
          {t.items.length === 0 && <tr><td colSpan={2} className="text-muted">None.</td></tr>}
          {t.items.map((i: any) => <tr key={i.input_id}><td>{i.description}</td><td className="num">{money(i.value, t.currency)}</td></tr>)}
          <tr className="font-semibold"><td>Total</td><td className="num">{money(t.total, t.currency)}</td></tr>
        </tbody>
      </table></div>
      <dl className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
        <div><dt className="label">Ex-works price</dt><dd className="tabular-nums">{money(t.ex_works_price, t.currency)}</dd></div>
        <div><dt className="label">Share</dt><dd className="tabular-nums">{t.share_is_lower_bound ? 'Cannot be calculated' : `${t.share_display}%`}</dd></div>
        <div><dt className="label">Limit (draft text)</dt><dd className="tabular-nums">{t.limit_percent}%</dd></div>
        <div><dt className="label">Margin</dt><dd className="tabular-nums">{t.share_is_lower_bound || t.margin_pp_display == null ? '—' : `${t.margin_pp_display} pp`}</dd></div>
      </dl>
      <p className="mt-3 note">Exact test: {t.comparison ?? '—'}. Valuation basis: customs value (Annex 2, Art. 1(y)).
        {t.alternative?.differs ? ' With FOB values the result is different.' : ''}{t.unresolved_ids?.length > 0 ? ` Not counted: ${t.unresolved_ids.join(', ')}.` : ''}</p>
    </Section>
  )
}

export function Findings({ result, onRule }: { result: any; onRule: (id: string) => void }) {
  const [filter, setFilter] = useState<string[]>(['critical', 'major', 'minor'])
  const shown = useMemo(() => result.findings.filter((f: any) => filter.includes(f.severity)), [result, filter])
  const n = (s: string) => result.findings.filter((f: any) => f.severity === s).length
  return (
    <Section kicker="Gap analysis" title="Findings"
      right={<div role="group" aria-label="Filter by severity" className="flex flex-wrap gap-1.5">
        {(['critical', 'major', 'minor'] as const).map(s => { const S = SEV[s]; return (
          <button key={s} aria-pressed={filter.includes(s)} onClick={() => setFilter(f => f.includes(s) ? f.filter(x => x !== s) : [...f, s])}
            className={`chip !text-sm ${filter.includes(s) ? S.cls : 'border-line text-muted'}`}><S.Icon size={12} />{S.label} <span className="tabular-nums">{n(s)}</span></button>) })}
      </div>}>
      {shown.length === 0 && <p className="note">No findings.</p>}
      <ol className="space-y-3">{shown.map((f: any) => (
        <li key={f.id} className="rounded-md border border-line p-4">
          <div className="flex flex-wrap items-center gap-2"><Severity s={f.severity} /><span className="font-semibold">{f.title}</span>
</div>
          <p className="mt-2 text-sm">{f.explanation}</p>
          <p className="mt-2 note">Source: {f.rule_ids.map((id: string, k: number) =>
            <button key={id} onClick={() => onRule(id)} className="text-accent hover:underline mr-3">{f.provisions[k]}</button>)}</p>
        </li>))}</ol>
      {result.notes?.length > 0 && <p className="mt-3 text-sm rounded-md border border-minor/50 p-3">The recipe contains wheat flour of Chapter 11. The Ex-Chapter 19 condition on wheat is not applied (group decision); the heading 19.01 row applies.</p>}
    </Section>
  )
}

export function InfoRequest({ result, title = 'Information we need from you' }: { result: any; title?: string }) {
  const [copied, setCopied] = useState(false)
  if (!result.missing_info_request) return null
  return (
    <Section title={title} right={<button className="btn" onClick={() => { navigator.clipboard?.writeText(result.missing_info_request); setCopied(true) }}><Copy />{copied ? 'Copied' : 'Copy'}</button>}>
      <pre className="pre !font-sans !text-sm !bg-transparent !border-0 !p-0">{result.missing_info_request}</pre>
    </Section>
  )
}
