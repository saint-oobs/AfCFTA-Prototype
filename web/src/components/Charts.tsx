import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Check, X } from './icons'

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

const RESULT_STYLE: Record<string, string> = {
  'Likely to qualify': 'border-ok text-ok', 'Likely not to qualify': 'border-crit text-crit', 'Further information required': 'border-major text-major' }
const SHORT: Record<string, string> = { 'Likely to qualify': 'Likely', 'Likely not to qualify': 'Likely not', 'Further information required': 'Further info' }

export function CaseTiles({ tiles }: { tiles: { case_id: string; set: string; result: string; sub_reasons: string[]; agrees: boolean }[] }) {
  const sets = [...new Set(tiles.map(t => t.set))]
  return (
    <div className="space-y-4">
      {sets.map(set => (
        <div key={set}><p className="label mb-2">{set}</p>
          <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-7 gap-2">
            {tiles.filter(t => t.set === set).map(t => (
              <Link key={t.case_id} to={`/navigator/${t.case_id}/adviser`} title={`${t.case_id}: ${t.result}${t.agrees ? ', agrees with the answer key' : ', does not agree with the answer key'}`}
                className={`rounded-md border-2 p-2 text-center hover:-translate-y-0.5 transition-transform ${RESULT_STYLE[t.result]}`}>
                <span className="block text-sm font-semibold text-ink">{t.case_id}</span>
                <span className="block text-[11px] leading-tight">{SHORT[t.result]}</span>
                <span className={`mt-1 inline-flex ${t.agrees ? 'text-ok' : 'text-crit'}`}>{t.agrees ? <Check size={14} /> : <X size={14} />}</span>
              </Link>))}
          </div>
        </div>))}
      <div className="flex flex-wrap gap-4 text-xs text-muted">
        {Object.entries(SHORT).map(([k, v]) => <span key={k} className="flex items-center gap-1.5"><i className={`inline-block w-3 h-3 rounded-sm border-2 ${RESULT_STYLE[k]}`} />{v}</span>)}
        <span className="flex items-center gap-1 text-ok"><Check size={12} />agrees with the answer key</span>
      </div>
    </div>
  )
}

export function DeficiencyChart({ data }: { data: { type: string; count: number }[] }) {
  const { tip, on } = useTip()
  const max = Math.max(1, ...data.map(d => d.count)), W = 560, left = 270, rowH = 26, barW = W - left - 40
  return (
    <div className="chart relative">
      <svg viewBox={`0 0 ${W} ${data.length * rowH + 4}`} className="w-full" role="img" aria-label="SME documentation deficiencies by type">
        {data.map((d, i) => {
          const y = i * rowH + 2
          return <g key={d.type} {...on(`${d.type}: ${d.count}`)}>
            <text x={left - 8} y={y + 15} textAnchor="end" className="fill-ink text-[11px]">{d.type}</text>
            <rect x={left} y={y + 3} width={Math.max(4, barW * d.count / max)} height={16} rx={4} fill="rgb(var(--s1))" />
            <text x={left + barW * d.count / max + 6} y={y + 15} className="fill-muted text-[11px] tabular-nums">{d.count}</text>
          </g>
        })}
      </svg>
      <Tip tip={tip} />
    </div>
  )
}

export function ConfusionChart({ labels, m }: { labels: string[]; m: Record<string, Record<string, number>> }) {
  const max = Math.max(1, ...labels.flatMap(e => labels.map(o => m[e][o])))
  const short = (s: string) => s.replace('Further information required', 'Further info').replace('Likely not to qualify', 'Likely not').replace('Likely to qualify', 'Likely')
  return (
    <div className="overflow-x-auto"><table className="text-sm border-separate border-spacing-[2px]" aria-label="Expected result (rows) against tool result (columns)">
      <thead><tr><th className="text-left note pr-2">Expected ↓ / Tool →</th>{labels.map(o => <th key={o} className="note px-2 font-medium">{short(o)}</th>)}</tr></thead>
      <tbody>{labels.map(e => <tr key={e}><th className="text-left font-medium pr-2 whitespace-nowrap">{short(e)}</th>
        {labels.map(o => { const v = m[e][o]; return <td key={o} title={`Expected ${e}, tool ${o}: ${v}`} className="w-24 h-12 !text-center rounded tabular-nums"
          style={{ background: v ? `rgb(var(--s1) / ${0.15 + 0.7 * v / max})` : 'rgb(var(--panel))', color: v / max > 0.5 ? 'white' : 'rgb(var(--ink))' }}>{v}</td> })}</tr>)}</tbody>
    </table></div>
  )
}

export function TranscriptionChart({ data }: { data: { group: string; fields: number; correct: number; flagged_unreadable: number; wrong: number }[] }) {
  const segs = [['correct', 'bg-ok', 'Read correctly'], ['flagged_unreadable', 'bg-major', 'Flagged as unreadable'], ['wrong', 'bg-crit', 'Read wrongly']] as const
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 text-xs text-muted">{segs.map(([, c, l]) => <span key={l} className="flex items-center gap-1.5"><i className={`inline-block w-3 h-3 rounded-sm ${c}`} />{l}</span>)}</div>
      {data.map(d => (
        <div key={d.group}>
          <div className="flex justify-between text-sm mb-1"><span className="font-medium">{d.group}</span>
            <span className="text-muted tabular-nums">{d.correct} correct · {d.flagged_unreadable} flagged · {d.wrong} wrong · {d.fields} values</span></div>
          <div className="flex h-3 rounded-full overflow-hidden bg-panel gap-[2px]">
            {segs.map(([k, c, l]) => { const v = (d as any)[k] as number; return v ? <div key={k} className={c} style={{ width: `${(100 * v) / d.fields}%` }} title={`${l}: ${v}`} /> : null })}
          </div>
        </div>))}
    </div>
  )
}
