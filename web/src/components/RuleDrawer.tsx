import { useEffect, useRef } from 'react'

export default function RuleDrawer({ rule, onClose }: { rule: any; onClose: () => void }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!rule) return
    ref.current?.focus()
    const f = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', f); return () => window.removeEventListener('keydown', f)
  }, [rule])
  if (!rule) return null
  const draft = /draft|not applied|interpretation|outstanding/i.test(rule.legal_status)
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <div ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={`Rule ${rule.id}`}
        className="h-full w-full max-w-lg overflow-auto bg-surface border-l border-line p-6 text-sm" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-start gap-4"><div><p className="label">{rule.id}</p><h2 className="h2">{rule.title}</h2></div>
          <button className="btn !px-3" onClick={onClose} aria-label="Close">✕</button></div>
        <p className={`mt-3 chip ${draft ? 'text-major border-major/40' : 'text-ok border-ok/40'}`}>{rule.legal_status}</p>
        <blockquote className="mt-4 border-l-2 border-accent pl-4 text-base leading-relaxed">{rule.text}</blockquote>
        <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
          <div><dt className="label">Provision</dt><dd>{rule.provision}</dd></div>
          <div><dt className="label">Page</dt><dd>{rule.page}</dd></div>
          <div className="col-span-2"><dt className="label">Source file</dt><dd className="break-all">{rule.source_file}</dd></div>
          <div><dt className="label">Version / date</dt><dd>{rule.version_date}</dd></div>
          <div><dt className="label">Applied by engine</dt><dd>{rule.applied ? 'yes' : 'no (reference)'}</dd></div>
          <div className="col-span-2"><dt className="label">Engine behaviour</dt><dd>{rule.engine_behaviour}</dd></div>
          {rule.notes && <div className="col-span-2"><dt className="label">Notes</dt><dd>{rule.notes}</dd></div>}
        </dl>
      </div>
    </div>
  )
}
