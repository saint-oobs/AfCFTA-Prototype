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

// Severity palette: red / orange / yellow; neutral grey for empty cells, green for matches.
const RED = '#d64545', ORANGE = '#f08c2e', YELLOW = '#f2c94c', GREEN = '#2f9e6b'
export const SEV_INFO = [
  ['critical', RED, 'Critical', 'The product is likely not to meet the rules of origin because of this gap.'],
  ['major', ORANGE, 'Major', 'Information is missing or contradictory. Tessera needs it from the SME before it can say whether the product qualifies.'],
  ['minor', YELLOW, 'Minor', 'A small gap in the paperwork. It does not change the outcome, but the SME should fix it before applying.'],
] as const

export function DeficiencyChart({ data }: { data: { type: string; count: number; critical: number; major: number; minor: number }[] }) {
  const max = Math.max(1, ...data.map(d => d.count))
  return (
    <div>
      <ul className="grid gap-1.5 mb-4 text-sm">{SEV_INFO.map(([k, c, l, d]) => <li key={k} className="flex gap-2 items-start">
        <span className="mt-1 inline-block h-3 w-3 shrink-0 rounded-sm" style={{ background: c }} /><span><b>{l}:</b> <span className="text-muted">{d}</span></span></li>)}</ul>
      <div role="img" aria-label="SME documentation deficiencies by type and severity" className="grid grid-cols-[minmax(0,11rem)_1fr] gap-x-3 gap-y-2 text-xs items-center">
        {data.map(d => <div key={d.type} className="contents">
          <span className="leading-tight">{d.type}</span>
          <span className="flex items-center gap-2">
            <span className="flex h-3.5 gap-[2px] rounded-sm bg-panel" style={{ width: `${(85 * d.count) / max}%` }}>
              {SEV_INFO.map(([k, c, l]) => { const v = (d as any)[k] as number; return v ? <span key={k} title={`${d.type}: ${v} ${l.toLowerCase()}`} className="h-full rounded-sm" style={{ background: c, flex: v }} /> : null })}
            </span><span className="tabular-nums text-muted">{d.count}</span></span>
        </div>)}
      </div>
    </div>
  )
}

export function ConfusionChart({ labels, m }: { labels: string[]; m: Record<string, Record<string, number>> }) {
  return (
    <div className="overflow-x-auto"><table className="text-sm border-separate border-spacing-1" aria-label="Expected outcome (rows) against Tessera outcome (columns)">
      <thead><tr><th className="text-left note pr-2 align-bottom font-normal">Expected ↓ · Tessera →</th>{labels.map(o => <th key={o} className="text-left note px-2 font-medium align-bottom w-28">{o.replace(' required', '')}</th>)}</tr></thead>
      <tbody>{labels.map(e => <tr key={e}><th className="text-left font-medium pr-3 whitespace-nowrap">{e.replace(' required', '')}</th>
        {labels.map(o => {
          const v = m[e][o], diag = e === o
          const style = v ? { background: diag ? GREEN : RED, color: 'white' } : { background: 'rgb(var(--panel))', color: 'rgb(var(--muted))' }
          return <td key={o} title={`Expected ${e}, Tessera ${o}: ${v}`} style={style}
            className={`h-14 px-3 rounded-md tabular-nums ${v ? 'font-semibold' : ''}`}>
            <span className="inline-flex items-center gap-1">{diag && v ? <Check size={14} /> : !diag && v ? <X size={14} /> : null}{v}</span></td>
        })}</tr>)}</tbody>
    </table></div>
  )
}

/** One compact matrix: record format (rows) × language (columns). */
export function TranscriptionMatrix({ data }: { data: { format: string; language: string; cases: number; fields: number; correct: number; flagged_unreadable: number; wrong: number }[] }) {
  const cell = (f: string, l: string) => data.find(d => d.format === f && d.language === l)
  const tot = data.reduce((a, d) => ({ fields: a.fields + d.fields, correct: a.correct + d.correct, flagged: a.flagged + d.flagged_unreadable, wrong: a.wrong + d.wrong }), { fields: 0, correct: 0, flagged: 0, wrong: 0 })
  return (
    <div className="grid lg:grid-cols-[1fr_16rem] gap-6 items-start">
      <div className="overflow-x-auto"><table className="text-sm border-separate border-spacing-1 w-full" aria-label="Values read correctly by record type">
        <thead><tr><th />{['English', 'multilingual'].map(l => <th key={l} className="text-left note font-medium px-3 pb-1">{l === 'English' ? 'English' : 'Multilingual'}</th>)}</tr></thead>
        <tbody>{['typed', 'handwritten'].map(f => <tr key={f}><th className="text-left font-medium pr-3 whitespace-nowrap">{f === 'typed' ? 'Typed' : 'Handwritten'}</th>
          {['English', 'multilingual'].map(l => { const d = cell(f, l)
            if (!d || !d.cases) return <td key={l} className="rounded-md bg-panel px-3 py-3 note">No case</td>
            const pct = (100 * d.correct) / d.fields
            return <td key={l} className="rounded-md border border-line px-3 py-3 align-top">
              <p><span className="text-xl font-semibold tabular-nums">{pct.toFixed(pct === 100 ? 0 : 1)}%</span> <span className="note">read correctly</span></p>
              <p className="note mt-0.5 tabular-nums">{d.correct} of {d.fields} values · {d.cases} case{d.cases > 1 ? 's' : ''}</p>
              {(d.flagged_unreadable > 0 || d.wrong > 0) && <p className="mt-1 text-xs tabular-nums">
                {d.flagged_unreadable > 0 && <span className="inline-flex items-center gap-1 mr-3"><span className="h-2 w-2 rounded-full" style={{ background: YELLOW }} />{d.flagged_unreadable} flagged unreadable</span>}
                {d.wrong > 0 && <span className="inline-flex items-center gap-1"><span className="h-2 w-2 rounded-full" style={{ background: RED }} />{d.wrong} read wrongly</span>}</p>}
            </td> })}</tr>)}</tbody>
      </table></div>
      <div className="rounded-lg bg-panel p-4 text-sm">
        <p className="label mb-2">All records</p>
        <p><span className="text-2xl font-semibold tabular-nums">{tot.correct}</span> <span className="note">of {tot.fields} values read correctly</span></p>
        <p className="mt-2">{tot.flagged} unreadable values were flagged, not guessed. {tot.wrong === 0 ? 'No value was read wrongly.' : `${tot.wrong} value(s) were read wrongly.`}</p>
      </div>
    </div>
  )
}
