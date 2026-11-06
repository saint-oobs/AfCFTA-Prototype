import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getTestLog } from '../lib/data'
import { PageHead, Section } from '../components/ui'
import { ConfusionChart, DeficiencyChart, TranscriptionMatrix } from '../components/Charts'
import { download, toCSV } from '../lib/csv'
import { Download } from '../components/icons'

export default function TestLog() {
  const [d, setD] = useState<any>(null)
  useEffect(() => { getTestLog().then(setD) }, [])
  if (!d) return <p className="p-8 note">Loading…</p>
  const s = d.success
  const total = s.deficiencies.reduce((a: number, x: any) => a + x.count, 0)
  const agree = s.tiles.filter((t: any) => t.agrees).length
  const csv = () => download('tessera_test_log.csv', toCSV([
    ...d.tests.flatMap((t: any) => t.cases.map((c: any) => ({ Set: 'Prototype test log', '#': t['#'], 'Case type': t.case_type, Product: `${t.product} (${t.hs})`, Case: c.case_id, 'Scenario / input': c.scenario, 'Expected outcome': c.expected }))),
    ...d.evaluation_cases.map((c: any) => ({ Set: 'Miscellaneous test logs', '#': '', 'Case type': 'Miscellaneous', Product: c.product, Case: c.case_id, 'Scenario / input': c.scenario, 'Expected outcome': c.expected })),
  ]))
  return (
    <>
      <PageHead title="Test log" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 space-y-6">
        <Section title="Prototype test log" right={<button className="btn" onClick={csv}><Download />Export CSV</button>}>
          <div className="overflow-x-auto"><table className="data">
            <thead><tr><th>#</th><th>Case type</th><th>Product</th><th>Case</th><th>Scenario / input</th><th>Expected outcome</th></tr></thead>
            <tbody>{d.tests.flatMap((t: any) => t.cases.map((c: any, k: number) => {
              const last = k === t.cases.length - 1
              const cell = last ? '' : '!border-b !border-dashed'
              return <tr key={c.case_id}>
                {k === 0 && <><td rowSpan={t.cases.length}>{t['#']}</td><td rowSpan={t.cases.length} className="whitespace-nowrap">{t.case_type}</td>
                  <td rowSpan={t.cases.length} className="min-w-[150px]">{t.product}<span className="block note tabular-nums">HS {t.hs}</span></td></>}
                <td className={cell}><Link className="text-accent font-medium hover:underline" to={`/navigator/${c.case_id}/inputs`}>{c.case_id}</Link></td>
                <td className={`min-w-[280px] ${cell}`}>{c.scenario}</td>
                <td className={`min-w-[190px] ${cell}`}>{c.expected}</td>
              </tr>
            }))}</tbody>
          </table></div>
        </Section>

        <Section title="Miscellaneous set test log">
          <div className="overflow-x-auto"><table className="data">
            <thead><tr><th>Case</th><th>What the SME uploaded</th><th>Tool result</th></tr></thead>
            <tbody>{d.evaluation_cases.map((c: any) => <tr key={c.case_id}><td><Link className="text-accent font-medium hover:underline" to={`/navigator/${c.case_id}/inputs`}>{c.case_id}</Link></td>
              <td>{c.scenario}</td><td className="min-w-[220px]">{c.observed}{c.sub ? <span className="block note">{c.sub}</span> : null}</td></tr>)}</tbody>
          </table></div>
        </Section>

        <section>
          <h2 className="h2 mb-4">Results against the success criteria</h2>
          <div className="grid lg:grid-cols-2 gap-4">
            <Section title="Assessment accuracy">
              <p className="mb-4"><span className="text-3xl font-semibold tabular-nums">{agree}</span> <span className="text-sm">of {s.tiles.length} Tessera results match the expected outcome of the AfCFTA application</span></p>
              <ConfusionChart labels={s.labels} m={s.confusion} />
              <p className="note mt-3">Rows: expected outcome. Columns: Tessera’s outcome. Matches lie on the diagonal; any number off the diagonal would be a mismatch.</p>
            </Section>
            <Section title="SME documentation deficiencies">
              <p className="mb-3"><span className="text-3xl font-semibold tabular-nums">{total}</span> <span className="text-sm">deficiencies reported</span></p>
              <DeficiencyChart data={s.deficiencies} />
            </Section>
            <div className="lg:col-span-2"><Section title="Reading the records (key assumption)"><TranscriptionMatrix data={s.transcription} /></Section></div>
          </div>
        </section>
      </div>
    </>
  )
}
