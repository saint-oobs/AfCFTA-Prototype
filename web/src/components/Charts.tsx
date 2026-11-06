import { useState } from 'react'
import { Check, Help, X } from './icons'

// Small SVG charts. Colours: --s1 (current) / --s2 (run 1) categorical pair, validated with the dataviz validator.
function Tip({ tip }: { tip: { x: number; y: number; text: string } | null }) {
  if (!tip) return null
  return <div className="pointer-events-none absolute z-10 rounded-md border border-line bg-surface px-2 py-1 text-xs shadow" style={{ left: tip.x, top: tip.y }}>{tip.text}</div>
}
function useTip() {
  const [tip, setTip] = useState<{ x: number; y: number; text: string } | null>(null)
  const on = (text: string) => ({
    onMouseMove: (e: React.MouseEvent) => { const r = (e.currentTarget as Element).closest('.chart')!.getBoundingClientRect(); setTip({ x: e.clientX - r.left + 12, y: e.clientY - r.top + 12, text }) },
    onMouseLeave: () => setTip(null), onFocus: () => setTip({ x: 8, y: 0, text }), onBlur: () => setTip(null), tabIndex: 0, 'aria-label': text,
  })
  return { tip, on }
}

export const SEV_INFO = [
  ['critical', 'rgb(var(--crit))', 'Critical', 'On its own, the product is likely not to qualify.'],
  ['major', '#d39b17', 'Major', 'No result is possible until the SME fixes it.'],
  ['minor', 'rgb(var(--minor))', 'Minor', 'The result does not change, but the SME should fix it before applying.'],
] as const

export function DeficiencyChart({ data }: { data: { type: string; count: number; critical: number; major: number; minor: number }[] }) {
  const max = Math.max(1, ...data.map(d => d.count))
  return (
    <div>
      <ul className="grid gap-1.5 mb-4 text-sm">{SEV_INFO.map(([k, c, l, d]) => <li key={k} className="flex gap-2 items-start">
        <span className="mt-1 inline-block h-3 w-3 shrink-0 rounded-sm" style={{ background: c }} /><span><b>{l}:</b> <span className="text-muted">{d}</span></span></li>)}</ul>
      <div role="img" aria-label="SME documentation deficiencies by type and severity" className="grid grid-cols-[minmax(0,11rem)_1fr] gap-x-3 gap-y-2 text-xs items-center">
        {data.map(d => <div key={d.type} className="contents">
          <span className="text-right leading-tight">{d.type}</span>
          <span className="flex items-center gap-2">
            <span className="flex h-3.5 gap-[2px]" style={{ width: `${(85 * d.count) / max}%` }}>
              {SEV_INFO.map(([k, c, l]) => { const v = (d as any)[k] as number; return v ? <span key={k} title={`${d.type}: ${v} ${l.toLowerCase()}`} className="h-full rounded-sm" style={{ background: c, flex: v }} /> : null })}
            </span><span className="tabular-nums text-muted">{d.count}</span></span>
        </div>)}
      </div>
    </div>
  )
}

export function ConfusionChart({ labels, m }: { labels: string[]; m: Record<string, Record<string, number>> }) {
  const short = (s: string) => s.replace('Further information required', 'Further information').replace('Likely not to qualify', 'Likely not to qualify').replace('Likely to qualify', 'Likely to qualify')
  return (
    <div className="overflow-x-auto"><table className="text-sm border-separate border-spacing-1" aria-label="Expected assessment (rows) against Tessera result (columns)">
      <thead><tr><th className="text-left note pr-2 align-bottom">Expected ↓ · Tessera →</th>{labels.map(o => <th key={o} className="note px-2 font-medium align-bottom w-28">{short(o)}</th>)}</tr></thead>
      <tbody>{labels.map(e => <tr key={e}><th className="text-left font-medium pr-3 whitespace-nowrap">{short(e)}</th>
        {labels.map(o => {
          const v = m[e][o], diag = e === o
          return <td key={o} title={`Expected ${e}, Tessera ${o}: ${v}`}
            className={`h-14 !text-center rounded-md tabular-nums font-semibold ${diag ? (v ? 'bg-ok/15 text-ok' : 'bg-panel text-muted') : v ? 'bg-crit/15 text-crit' : 'bg-panel text-muted font-normal'}`}>
            <span className="inline-flex items-center gap-1">{diag && v ? <Check size={14} /> : !diag && v ? <X size={14} /> : null}{v}</span></td>
        })}</tr>)}</tbody>
    </table></div>
  )
}

export function TranscriptionGrid({ data }: { data: { format: string; language: string; cases: number; fields: number; correct: number; flagged_unreadable: number; wrong: number }[] }) {
  return (
    <div className="grid sm:grid-cols-2 gap-3">
      {data.map(d => {
        const pct = d.fields ? (100 * d.correct) / d.fields : 0
        return <div key={d.format + d.language} className="rounded-lg border border-line p-4">
          <p className="label">{d.format === 'handwritten' ? 'Handwritten' : 'Typed'} records · {d.language}</p>
          {d.cases === 0 ? <p className="note mt-2">No case of this type.</p> : <>
            <p className="mt-1"><span className="text-2xl font-semibold tabular-nums">{d.correct}</span> <span className="text-sm text-muted">of {d.fields} values read correctly · {d.cases} case{d.cases > 1 ? 's' : ''}</span></p>
            <div className="mt-2 h-2 rounded-full bg-panel overflow-hidden" role="img" aria-label={`${pct.toFixed(1)}% read correctly`}><div className="h-full rounded-full bg-accent" style={{ width: `${pct}%` }} /></div>
            <ul className="mt-3 text-sm space-y-1">
              <li className="flex items-center gap-2"><Help size={14} className={d.flagged_unreadable ? 'text-major' : 'text-muted'} />{d.flagged_unreadable} value{d.flagged_unreadable === 1 ? '' : 's'} flagged as unreadable (not guessed)</li>
              <li className="flex items-center gap-2"><X size={14} className={d.wrong ? 'text-crit' : 'text-muted'} />{d.wrong} value{d.wrong === 1 ? '' : 's'} read wrongly</li>
            </ul></>}
        </div>
      })}
    </div>
  )
}
