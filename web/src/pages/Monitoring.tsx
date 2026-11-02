import { useSyncExternalStore } from 'react'
import { PageHead, Section } from '../components/ui'
import { log } from '../lib/log'
import { download, toCSV } from '../lib/csv'
import { Download } from '../components/icons'

const KIND: Record<string, string> = { override: 'Correction', rerun: 'New run', bug_report: 'Bug report', error: 'Error', clarification: 'Request to the SME', missing_info: 'Request to the SME', approved: 'Approved', release: 'New version' }

export default function Monitoring() {
  const events = useSyncExternalStore(log.subscribe, log.all)
  const version = useSyncExternalStore(log.subscribe, log.version)
  const counts = Object.entries(events.reduce((a: Record<string, number>, e) => { const k = KIND[e.kind] ?? e.kind; a[k] = (a[k] ?? 0) + 1; return a }, {}))
  function exportAgg() {
    const agg = new Map<string, number>()
    events.forEach(e => { const k = [KIND[e.kind], e.error_type ?? '', e.field ?? '', e.model_version].join('|'); agg.set(k, (agg.get(k) ?? 0) + 1) })
    const rows = [...agg].map(([k, n]) => { const [event, error_type, field, v] = k.split('|'); return { event, error_type, field, version: v, count: n } })
    download('tessera_monitoring_counts.csv', toCSV(rows.length ? rows : [{ event: '', error_type: '', field: '', version: '', count: 0 }]))
  }
  return (
    <>
      <PageHead kicker="Stage 6" title="Feedback and monitoring" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="card p-4"><p className="label">Model version</p><p className="text-2xl font-semibold mt-1 tabular-nums">{version}</p></div>
          {['Correction', 'Bug report', 'Error'].map(k => <div key={k} className="card p-4"><p className="label">{k}s</p><p className="text-2xl font-semibold mt-1 tabular-nums">{counts.find(c => c[0] === k)?.[1] ?? 0}</p></div>)}
        </div>
        <Section title="Event log" right={<div className="flex gap-2"><button className="btn" onClick={exportAgg}><Download />Export counts (CSV)</button><button className="btn" onClick={() => log.reset()}>Clear</button></div>}>
          <div className="overflow-x-auto"><table className="data">
            <thead><tr><th>Time</th><th>Case</th><th>Event</th><th>Detail</th><th>Version</th></tr></thead>
            <tbody>{events.length === 0 && <tr><td colSpan={5} className="note">No events.</td></tr>}
              {[...events].reverse().map((e, i) => <tr key={i}><td className="whitespace-nowrap tabular-nums">{e.ts.slice(0, 10)} {e.ts.slice(11, 19)}</td><td>{e.case_id}</td><td>{KIND[e.kind] ?? e.kind}</td><td>{e.detail}</td><td className="tabular-nums">{e.model_version}</td></tr>)}</tbody>
          </table></div>
        </Section>
      </div>
    </>
  )
}
