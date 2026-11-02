const base = import.meta.env.BASE_URL
const cache = new Map<string, Promise<any>>()
export function getJSON<T = any>(path: string): Promise<T> {
  if (!cache.has(path)) cache.set(path, fetch(base + path).then(r => { if (!r.ok) throw new Error(path); return r.json() }))
  return cache.get(path)!
}
export const getIndex = () => getJSON('data/index.json')
export const getCase = (id: string) => getJSON(`data/cases/${id}.json`)
export const getRules = () => getJSON('data/rules.json')
export const getTestLog = () => getJSON('data/test_log.json')
export const imageUrl = (caseId: string, docId: string) => `${base}data/images/${caseId}_${docId}.png`
