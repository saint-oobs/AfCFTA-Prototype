import anime from 'animejs'
export const reduced = () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
export function reveal(targets: any, delay = 0) {
  if (reduced() || !targets) return
  anime({ targets, opacity: [0, 1], translateY: [8, 0], duration: 520, delay: anime.stagger(70, { start: delay }), easing: 'easeOutCubic' })
}
export function countUp(el: HTMLElement | null, to: number, decimals = 0) {
  if (!el) return
  if (reduced()) { el.textContent = to.toFixed(decimals); return }
  const o = { v: 0 }
  anime({ targets: o, v: to, duration: 1100, easing: 'easeOutExpo', update: () => { el.textContent = o.v.toFixed(decimals) } })
}
