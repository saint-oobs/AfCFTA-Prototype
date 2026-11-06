import { ReactNode } from 'react'
import { Alert, Check, Help, Info, Octagon, X } from './icons'

export const SEV = {
  critical: { cls: 'text-crit border-crit/50 bg-crit/10', Icon: Octagon, label: 'Critical' },
  major: { cls: 'text-major border-major/50 bg-major/10', Icon: Alert, label: 'Major' },
  minor: { cls: 'text-minor border-minor/50 bg-minor/10', Icon: Info, label: 'Minor' },
  info: { cls: 'text-muted border-line', Icon: Info, label: 'Info' },
} as const

export function Severity({ s }: { s: keyof typeof SEV }) {
  const v = SEV[s] || SEV.info
  return <span className={`chip ${v.cls}`}><v.Icon size={12} />{v.label}</span>
}

const STATUS: Record<string, [string, any, string]> = {
  met: ['text-ok border-ok/50 bg-ok/10', Check, 'Met'], 'met via 15% tolerance': ['text-ok border-ok/50 bg-ok/10', Check, 'Met (15% limit)'],
  'not met': ['text-crit border-crit/50 bg-crit/10', X, 'Not met'], unclear: ['text-major border-major/50 bg-major/10', Help, 'Unclear'],
  'not assessed': ['text-muted border-line', Info, 'Not checked'],
}
export function Status({ s }: { s: string }) {
  const [cls, Icon, label] = STATUS[s] || ['text-muted border-line', Info, s]
  return <span className={`chip ${cls}`}><Icon size={12} />{label}</span>
}

export function Tag({ s }: { s: string }) {
  const cls = s === 'stated' ? 'text-ok border-ok/50' : s === 'inferred' ? 'text-minor border-minor/50' : 'text-major border-major/50'
  return <span className={`chip ${cls}`}>{s}</span>
}

export const OUTCOME_STYLE: Record<string, { cls: string; Icon: any }> = {
  'Likely to qualify': { cls: 'border-ok text-ok', Icon: Check },
  'Likely not to qualify': { cls: 'border-crit text-crit', Icon: X },
  'Further information required': { cls: 'border-major text-major', Icon: Help },
}
export const SUB: Record<string, string> = { missing: 'information is missing', contradictory: 'contradictory information', out_of_rule_base: 'HS code outside heading 19.01 or in doubt' }

export function Section({ title, kicker, children, right }: { title: string; kicker?: string; children: ReactNode; right?: ReactNode }) {
  return (
    <section className="card p-5">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>{kicker && <p className="label mb-1">{kicker}</p>}<h2 className="h2">{title}</h2></div>{right}
      </div>
      {children}
    </section>
  )
}

export function PageHead({ kicker, title, children }: { kicker?: string; title: string; children?: ReactNode }) {
  return <div className="mx-auto max-w-6xl px-4 sm:px-6 pt-8 pb-5">
    {kicker && <p className="label mb-2">{kicker}</p>}
    <h1 className="h1">{title}</h1>
    {children && <div className="mt-2 max-w-3xl lead">{children}</div>}
  </div>
}

export const STAGES = [
  ['1', 'Inputs and data', 'The SME provides: bill of materials, supplier declarations, production notes, costing sheet and invoice.'],
  ['2', 'AI task', 'The tool reads the records, puts the data into fixed fields, identifies the HS code and evaluates the production process.'],
  ['3', 'Model', 'The model uses RAG and bounded LLM agents, which is connected to the non-parametric knowledge base. This prototype uses a stub with a python code snippet.'],
  ['4', 'Output', 'The model compares the submitted data with the AfCFTA rules of origin. It returns one of three outcomes: the application is likely to qualify, the application is unlikely to qualify, or an error flags missing or contradictory data. Each outcome comes with the reasons behind it and any gaps that were found.'],
  ['5', 'Human decision', 'A trade adviser checks the HS code against the SME’s documents.'],
  ['6', 'Feedback and monitoring', 'The SME and the trade adviser report hallucinations and data that the model extracted or identified wrongly. The development team receives this feedback and releases an updated version of the model.'],
] as const

export const DISCLAIMER = 'Indicative pre-check only. It is not an origin decision. The National AfCFTA Approval Committee decides on origin and GRA Customs issues the certificate.'

// Date = 'compiled' in rules/rules.json. Update both when the rule data is refreshed.
export const RULE_DATA_SHORT = 'AfCFTA guidelines as of 1 November 2026'

