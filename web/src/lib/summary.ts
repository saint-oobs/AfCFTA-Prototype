// Same template as adapter/stub.py explain(): SME summary in plain language, used after an in-browser re-run.
export function smeSummary(r: any): string {
  const o = r.outcome, t = r.components.tolerance, reqs = r.requirements || []
  const head: Record<string, string> = {
    'Likely to qualify': 'Your product is likely to meet the AfCFTA rules of origin.',
    'Likely not to qualify': 'Your product is likely NOT to meet the AfCFTA rules of origin.',
    'Further information required': 'We cannot give a result yet. We need more information from you.',
  }
  const lines = [head[o.label], '', 'Main reasons:']
  const bad = reqs.filter((q: any) => q.status === 'not met' || q.status === 'unclear')
  ;(bad.length ? bad.slice(0, 3) : reqs.filter((q: any) => q.status === 'met').slice(1, 3)).forEach((q: any) => lines.push(`- ${q.evidence}`))
  if (t?.status === 'met via 15% tolerance') {
    const margin = String(t.margin_pp_display).replace(/0+$/, '').replace(/\.$/, '') || '0'
    lines.push('', `Note: the 15% limit is the AfCFTA tolerance rule (EX.CL/1329(XL), Annex, item 3). Your margin is ${margin} percentage points. A change in prices or recipe can change the result.`)
  }
  const fixes = [...new Set(r.findings.filter((f: any) => f.severity === 'critical' || f.severity === 'major').map((f: any) => f.sme_action || f.fix))].slice(0, 3) as string[]
  lines.push('', 'What to do next:')
  if (fixes.length) fixes.forEach(f => lines.push(`- ${f}`)); else lines.push('- Keep your supplier declarations, invoices and production records together.')
  lines.push('- You decide whether to apply. GRA Customs and the National AfCFTA Approval Committee make the official decision.')
  return lines.join('\n')
}
