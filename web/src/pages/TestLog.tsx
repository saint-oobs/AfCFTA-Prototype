import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getTestLog } from '../lib/data'
import { PageHead, Section, Severity } from '../components/ui'
import { CaseTiles, ConfusionChart, DeficiencyChart, TranscriptionChart } from '../components/Charts'
import { download, toCSV } from '../lib/csv'
import { Download } from '../components/icons'

export default function TestLog() {
  const [d, setD] = useState<any>(null)
  useEffect(() => { getTestLog().then(setD) }, [])
  if (!d) return <p className="p-8 note">Loading…</p>
  const s = d.success
  const total = s.deficiencies.reduce((a: number, x: any) => a + x.count, 0)
  const agree = s.tiles.filter((t: any) => t.agrees).length
  const csv = () => download('tessera_test_log.csv', toCSV(d.tests.flatMap((t: any) => t.cases.map((c: any) => ({ '#': t['#'], 'Case type': t.case_type, Product: `${t.product} (${t.hs})`, Case: c.case_id, 'Scenario / input': c.scenario, 'Expected outcome': c.expected })))))
  return (
    <>
      <PageHead title="Test log" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 space-y-6">
        <Section kicker="1 · Tests" title="Prototype test log" right={<button className="btn" onClick={csv}><Download />Export CSV</button>}>
          <div className="overflow-x-auto"><table className="data">
            <thead><tr><th>#</th><th>Case type</th><th>Product</th><th>Scenario / input</th><th>Expected outcome</th></tr></thead>
            <tbody>{d.tests.map((t: any) => (
              <tr key={t['#']}><td>{t['#']}</td><td className="whitespace-nowrap">{t.case_type}</td>
                <td className="min-w-[150px]">{t.product}<span className="block note tabular-nums">HS {t.hs}</span></td>
                <td className="min-w-[280px]"><ul className="space-y-1.5">{t.cases.map((c: any) => <li key={c.case_id} className="grid grid-cols-[42px_1fr] gap-2">
                  <Link className="text-accent font-medium hover:underline" to={`/navigator/${c.case_id}/inputs`}>{c.case_id}</Link><span>{c.scenario}</span></li>)}</ul></td>
                <td className="min-w-[200px]"><ul className="space-y-1.5">{t.cases.map((c: any) => <li key={c.case_id} className="grid grid-cols-[42px_1fr] gap-2">
                  <span className="text-muted">{t.cases.length > 1 ? c.case_id : ''}</span><span>{c.expected}</span></li>)}</ul></td></tr>))}</tbody>
          </table></div>
        </Section>

        <section>
          <p className="label mb-1">2 · Measured results</p><h2 className="h2 mb-4">Results against the success criteria</h2>
          <div className="grid lg:grid-cols-2 gap-4">
            <div className="lg:col-span-2"><Section title="Assessment accuracy" right={<p className="text-sm"><span className="text-2xl font-semibold tabular-nums">{agree}</span> of {s.tiles.length} cases agree with the answer key</p>}>
              <CaseTiles tiles={s.tiles} /></Section></div>
            <Section title="SME documentation deficiencies">
              <p><span className="text-3xl font-semibold tabular-nums">{total}</span> <span className="text-sm">deficiencies reported</span></p>
              <div className="flex flex-wrap gap-2 mt-2 mb-4">{(['critical', 'major', 'minor'] as const).map(k => <span key={k} className="inline-flex items-center gap-1.5 text-sm"><Severity s={k} /><span className="tabular-nums">{s.severity[k]}</span></span>)}</div>
              <DeficiencyChart data={s.deficiencies} />
            </Section>
            <Section title="Expected result against tool result"><ConfusionChart labels={s.labels} m={s.confusion} /><p className="note mt-3">All {s.tiles.length} cases. Cases on the diagonal agree with the answer key.</p></Section>
            <div className="lg:col-span-2"><Section title="Reading the records (key assumption)"><TranscriptionChart data={s.transcription} /></Section></div>
          </div>
        </section>

        <Section kicker="3 · Evaluation set" title="Missing and contradictory information">
          <div className="overflow-x-auto"><table className="data">
            <thead><tr><th>Case</th><th>What the SME uploaded</th><th>Tool result</th></tr></thead>
            <tbody>{d.evaluation_cases.map((c: any) => <tr key={c.case_id}><td><Link className="text-accent font-medium hover:underline" to={`/navigator/${c.case_id}/adviser`}>{c.case_id}</Link></td>
              <td>{c.scenario}</td><td className="min-w-[200px]">{c.observed}{c.sub ? <span className="block note">{c.sub}</span> : null}</td></tr>)}</tbody>
          </table></div>
        </Section>
      </div>
    </>
  )
}
