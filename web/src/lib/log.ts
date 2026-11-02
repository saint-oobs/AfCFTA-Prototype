// Stage 6 – feedback and monitoring log (in memory, mirrored to localStorage when available).
export type LogEvent = { ts: string; case_id: string; kind: 'override' | 'rerun' | 'bug_report' | 'error' | 'clarification' | 'missing_info' | 'approved' | 'release'
  error_type?: string; field?: string; detail: string; model_version: string }
const KEY = 'coo-nav-log-v1'
let events: LogEvent[] = (() => { try { return JSON.parse(localStorage.getItem(KEY) || '[]') } catch { return [] } })()
let version = (() => { try { return localStorage.getItem(KEY + '-ver') || '1.1.0' } catch { return '1.1.0' } })()
const subs = new Set<() => void>()
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(events)); localStorage.setItem(KEY + '-ver', version) } catch { /* storage unavailable */ } subs.forEach(f => f()) }
export const log = {
  all: () => events, version: () => version,
  add(e: Omit<LogEvent, 'ts' | 'model_version'>) { events = [...events, { ...e, ts: new Date().toISOString(), model_version: version }]; save() },
  count(error_type: string, field: string) { return events.filter(e => e.kind === 'override' && e.error_type === error_type && e.field === field).length },
  release(note: string) {
    const [a, b, c] = version.split('.').map(Number); version = `${a}.${b}.${c + 1}`
    events = [...events, { ts: new Date().toISOString(), case_id: '-', kind: 'release', detail: note, model_version: version }]; save()
  },
  reset() { events = []; version = '1.1.0'; save() },
  subscribe(f: () => void) { subs.add(f); return () => { subs.delete(f) } },
}
