import { useEffect, useRef } from 'react'
import anime from 'animejs'
import { reduced } from '../lib/motion'

// 7 x 7 mosaic. Accent tiles form the Tessera "T"; the tiles settle into place once, then a soft wave runs on hover.
const N = 7
const isT = (x: number, y: number) => (y === 1 && x >= 1 && x <= 5) || (x === 3 && y >= 2 && y <= 5)

export default function HeroMosaic() {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!ref.current || reduced()) return
    const tiles = ref.current.querySelectorAll('.tile')
    const a = anime({ targets: tiles, scale: [0.2, 1], opacity: [0, 1], rotate: [anime.random(-40, 40), 0], delay: anime.stagger(35, { grid: [N, N], from: 'center' }),
      duration: 700, easing: 'easeOutBack' })
    return () => a.pause()
  }, [])
  const wave = (i: number) => {
    if (reduced() || !ref.current) return
    anime({ targets: ref.current.querySelectorAll('.tile'), translateY: [{ value: -6, duration: 180 }, { value: 0, duration: 380 }],
      delay: anime.stagger(30, { grid: [N, N], from: i }), easing: 'easeOutSine' })
  }
  return (
    <div ref={ref} className="grid gap-1.5 w-full max-w-[340px] mx-auto aspect-square" style={{ gridTemplateColumns: `repeat(${N}, 1fr)` }} aria-hidden>
      {Array.from({ length: N * N }, (_, i) => {
        const x = i % N, y = Math.floor(i / N), t = isT(x, y)
        return <div key={i} className={`tile rounded-md ${t ? 'bg-accent' : (x + y) % 3 === 0 ? 'bg-accent/15' : 'bg-line/70'}`} onMouseEnter={() => wave(i)} />
      })}
    </div>
  )
}
