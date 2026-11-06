import { Requirements, ShareGauge, Stamp, InfoRequest } from './Result'
import { DISCLAIMER, RULE_DATA_SHORT, Section } from './ui'
import { useDecision } from './Adviser'
import { LogoMark } from './Logo'
import { Printer } from './icons'

export default function SmeView({ caseId, extracted, result, summary }: { caseId: string; extracted: any; result: any; summary: string }) {
  const decision = useDecision(caseId)
  const [head, ...rest] = summary.split('\n')
  const cut = rest.indexOf('What to do next:')
  const reasons = rest.slice(0, cut).filter(l => l)
  const actions = rest.slice(cut + 1).filter(l => l.startsWith('- '))
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 no-print">
        <p className={`text-sm font-medium ${decision ? 'text-ok' : 'text-major'}`}>Status: {decision ? `sent by the adviser on ${decision.ts.slice(0, 10)}` : 'in review by the adviser'}</p>
        <button className="btn" onClick={() => window.print()}><Printer />Print</button>
      </div>
      <article className="card p-6 sm:p-8">
        <header className="flex flex-wrap justify-between gap-4 border-b border-line pb-5">
          <div className="flex gap-3 items-start"><LogoMark size={36} /><div><p className="label">Tessera · rules of origin pre-check</p>
            <h2 className="h2 mt-1">{extracted?.exporter?.name ?? '—'}</h2></div></div>
          <Stamp result={result} small />
        </header>
        <dl className="grid sm:grid-cols-[1fr_auto] gap-4 text-sm mt-5">
          <div><dt className="label">Product</dt><dd>{extracted?.product?.description ?? '—'}</dd></div>
          <div><dt className="label">HS code</dt><dd className="tabular-nums">{extracted?.product?.declared_hs ?? '—'}</dd></div>
        </dl>
        <h3 className="h2 mt-6">{head}</h3>
        <div className="text-sm mt-2 space-y-1.5">{reasons.map((l, i) => l.startsWith('- ')
          ? <p key={i} className="pl-4 relative"><span className="absolute left-0 top-2 h-1.5 w-1.5 rounded-full bg-accent" />{l.slice(2)}</p>
          : <p key={i} className={l.endsWith(':') ? 'font-semibold' : 'rounded-md bg-panel p-3 mt-2'}>{l}</p>)}</div>
        <h3 className="h3 mt-6">What to do next</h3>
        <ol className="text-sm mt-2 space-y-1.5">{actions.map((a, i) => <li key={i} className="flex gap-3"><span className="grid place-items-center h-5 w-5 shrink-0 rounded-full bg-accent-soft text-accent text-xs font-semibold">{i + 1}</span>{a.slice(2)}</li>)}</ol>
      </article>
      <ShareGauge result={result} />
      <InfoRequest result={result} />
      <Section title="Check our reading of your documents">
        <p className="text-sm mb-3">If a statement in this table is wrong, tell us before you apply.</p>
        <Requirements result={result} sme />
      </Section>
      <p className="note">{DISCLAIMER} Rule data: {RULE_DATA_SHORT}.</p>
    </div>
  )
}
