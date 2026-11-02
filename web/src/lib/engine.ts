// Client for the Pyodide worker. Falls back to precomputed results if Pyodide cannot load.
export type EngineMode = 'loading' | 'pyodide' | 'precomputed'
let worker: Worker | null = null
let seq = 0
const pending = new Map<number, { res: (v: any) => void; rej: (e: any) => void }>()
let ready: Promise<{ version: string; python: string }> | null = null

function call(type: string, payload: any): Promise<any> {
  return new Promise((res, rej) => {
    const id = ++seq
    pending.set(id, { res, rej })
    worker!.postMessage({ id, type, payload })
  })
}

export function initEngine(): Promise<{ version: string; python: string }> {
  if (ready) return ready
  worker = new Worker(new URL('../worker/pyodide.worker.ts', import.meta.url))
  worker.onmessage = (e) => {
    const p = pending.get(e.data.id); if (!p) return
    pending.delete(e.data.id); e.data.ok ? p.res(e.data.result) : p.rej(new Error(e.data.error))
  }
  const base = new URL(import.meta.env.BASE_URL, window.location.href).href
  ready = Promise.race([
    call('init', { base }),
    new Promise<never>((_, rej) => setTimeout(() => rej(new Error('Pyodide did not load within 45 s')), 45000)),
  ])
  return ready
}
export const runEngine = (c: any, basis?: string) => call('assess', { case: c, basis })
export const checkCitations = (text: string) => call('cite', { text })
