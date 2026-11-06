import { Link } from 'react-router-dom'
import { useEffect, useRef, useState } from 'react'
import anime from 'animejs'
import HeroMosaic from '../components/HeroMosaic'
import { STAGES } from '../components/ui'
import { reduced } from '../lib/motion'
import { Activity, ArrowRight, Cpu, FileText, Scale, Scan, User } from '../components/icons'

export const TESTS = [
  ['1', 'Typical', 'Malt extract', '1901.90', 'Local and AfCFTA ingredients, full processing in Ghana.', 'T1'],
  ['2', 'Failure', 'Millet porridge mix', '1901.90', 'No eligible manufacturing process: only cleaning, grinding, mixing and packing.', 'T2'],
  ['3', 'Edge', 'Malted bread mix', '1901.20', 'Imported 19.01 premix at 14.9%, 15.0% and 15.1%, and two lots of 8% each.', 'T3a'],
  ['4', 'Edge / difficult', 'Cassava flour for baking', '1901.20', 'HS code in doubt: declared as a baking mix, but the description reads like plain ground cassava.', 'T4'],
  ['5', 'Key assumption', 'Infant cereal', '1901.10', 'Handwritten and multilingual records; one value cannot be read.', 'T5a'],
]

const ICONS = [FileText, Scan, Cpu, Scale, User, Activity]
const TASKS: [string, string][][] = [
  [['Data', 'The SME’s invoices, bills of materials, costing sheets and supplier records. The knowledge base holds the AfCFTA rules of origin and the HS schedules.']],
  [['Extraction', 'SME records come in many layouts, often handwritten or multilingual. Fixed templates fail on such records; a language model can read them.'],
   ['Classification', 'Most SMEs find HS classification difficult. The model suggests the HS code with the text it comes from, and the adviser confirms it.'],
   ['Process evaluation', 'Each production step is checked against the accepted operations in the AfCFTA guidelines.']],
  [['Retrieval (RAG)', 'The answer is grounded in the official legal text, not in the model’s memory. The knowledge base can be updated without retraining.'],
   ['Bounded agents', 'Instructions limit the model to the retrieved text and the extracted data. It flags gaps and does not guess.'],
   ['Exact calculation', 'Calculations such as the 15% limit run in plain code with exact numbers, not in the language model.']],
  [['Matching', 'The extracted values and steps are compared with the rule for heading 19.01.'],
   ['Generation', 'A plain-language summary and a list of gaps with actions for the SME.']],
  [['Human review', 'If the HS code is confirmed, the result is sent to the SME; if not, the SME is asked for more information.']],
  [['Error log', 'Every correction, new run and processing error is logged with the case and the model version.'], ['Bug reports', 'When the same error occurs twice, a bug report goes to the development team automatically.'], ['Support insights', 'Aggregated, de-identified data shows which documents SMEs most often get wrong, so the Centre can target its support.']],
]

function Pipeline() {
  const [active, setActive] = useState(0)
  const [auto, setAuto] = useState(true)
  const panel = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!auto || reduced()) return
    const t = setInterval(() => setActive(a => (a + 1) % STAGES.length), 4500)
    return () => clearInterval(t)
  }, [auto])
  useEffect(() => {
    if (panel.current && !reduced()) anime({ targets: panel.current.children, opacity: [0, 1], translateY: [6, 0], delay: anime.stagger(60), duration: 380, easing: 'easeOutQuad' })
  }, [active])
  const pick = (i: number) => { setAuto(false); setActive(i) }
  const Icon = ICONS[active]
  return (
    <div className="card p-5 sm:p-6">
      <div className="relative">
        <svg className="absolute left-0 right-0 top-6 h-1 w-full hidden sm:block" preserveAspectRatio="none" viewBox="0 0 100 2" aria-hidden>
          <line x1="4" y1="1" x2="96" y2="1" className="stroke-line" strokeWidth="2" vectorEffect="non-scaling-stroke" />
          <line x1="4" y1="1" x2={4 + (92 * active) / (STAGES.length - 1)} y2="1" className="stroke-accent flow-line" strokeWidth="2" vectorEffect="non-scaling-stroke" />
        </svg>
        <ol className="relative grid grid-cols-3 sm:grid-cols-6 gap-3" role="tablist" aria-label="Stages of the service">
          {STAGES.map(([n, t], i) => {
            const I = ICONS[i], on = i === active, done = i < active
            return <li key={n} className="flex flex-col items-center text-center">
              <button role="tab" aria-selected={on} onClick={() => pick(i)} onMouseEnter={() => pick(i)}
                className={`grid place-items-center h-12 w-12 rounded-xl border-2 transition-all ${on ? 'bg-accent border-accent text-white dark:text-[rgb(14,15,15)] scale-110 shadow' : done ? 'bg-accent-soft border-accent text-accent' : 'bg-surface border-line text-muted'}`}>
                <I size={20} /></button>
              <span className={`mt-2 text-xs font-semibold ${on ? 'text-accent' : 'text-muted'}`}>{n}. {t}</span>
            </li>
          })}
        </ol>
      </div>
      <div ref={panel} className="mt-6 grid md:grid-cols-[1fr_1.4fr] gap-6 border-t border-line pt-5" role="tabpanel">
        <div>
          <p className="label flex items-center gap-2"><Icon size={14} /> Stage {STAGES[active][0]}</p>
          <h3 className="h2 mt-1">{STAGES[active][1]}</h3>
          <p className="mt-2 text-sm text-muted">{STAGES[active][2]}</p>
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {TASKS[active].map(([t, d]) => (
            <div key={t} className="rounded-lg bg-panel p-4"><p className="text-sm font-semibold">{t}</p><p className="mt-1 text-sm text-muted">{d}</p></div>))}
        </div>
      </div>
    </div>
  )
}

export default function Landing() {
  return (
    <>
      <section className="border-b border-line">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-12 sm:py-16 grid lg:grid-cols-[1.2fr_1fr] gap-10 items-center">
          <div>
            <p className="label mb-3">AI Adoption and Innovation Centre · Ghana</p>
            <h1 className="text-5xl font-semibold tracking-tight">Tessera</h1>
            <p className="mt-3 text-xl">Know if your product meets the AfCFTA rules of origin before you apply.</p>
            <p className="mt-4 lead max-w-xl">Tessera checks food products of HS heading 19.01 against the AfCFTA rules of origin. It shows the likely result, the reasons and the missing information.</p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link to="/navigator/T1/inputs" className="btn-primary">Open the Navigator <ArrowRight /></Link>
              <Link to="/tests" className="btn">Test log</Link>
            </div>
          </div>
          <HeroMosaic />
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 sm:px-6 py-12">
        <h2 className="h2 mb-5">How Tessera works</h2>
        <Pipeline />
      </section>

      <section className="mx-auto max-w-6xl px-4 sm:px-6 pb-12">
        <h2 className="h2 mb-4">The rules that Tessera checks</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[['Heading rule', 'Ingredients from outside the AfCFTA must not themselves be products of heading 19.01. For example, imported wheat flour (heading 11.01) or milk powder (heading 04.02) is allowed; an imported premix or malt extract of heading 19.01 is not.'],
            ['15% tolerance', 'Exception to the heading rule: imported ingredients of heading 19.01 are still allowed if, together, they cost no more than 15% of the factory price (ex-works price) of the product.'],
            ['Eligible manufacturing processes', 'Mixing, grinding or packaging alone are not sufficient production processes for a certificate of origin under AfCFTA requirements. Real processing, such as cooking, roasting or drying, must take place in Ghana.']].map(([t, d]) => (
            <div key={t} className="card p-5"><p className="h3">{t}</p><p className="mt-2 text-sm">{d}</p></div>))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 sm:px-6">
        <h2 className="h2">Test cases</h2>
        <p className="note mt-1 mb-4">Each test uses a different product. Heading 19.01 has only three subheadings (1901.10, 1901.20 and 1901.90), so five tests cannot all have different codes.</p>
        <div className="card overflow-x-auto"><table className="data">
          <thead><tr><th>Test</th><th>Type</th><th>Product</th><th>HS code</th><th>What the test checks</th><th /></tr></thead>
          <tbody>{TESTS.map(([n, type, prod, hs, what, id]) => (
            <tr key={n}><td>{n}</td><td>{type}</td><td>{prod}</td><td className="tabular-nums">{hs}</td><td className="text-muted">{what}</td>
              <td><Link className="inline-flex items-center gap-1 text-accent font-medium hover:underline whitespace-nowrap" to={`/navigator/${id}/inputs`}>Open <ArrowRight size={14} /></Link></td></tr>))}</tbody>
        </table></div>
      </section>
    </>
  )
}
