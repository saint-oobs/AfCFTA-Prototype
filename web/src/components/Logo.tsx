// Tessera logo: nine mosaic tiles; the five accent tiles form a "T".
export function LogoMark({ size = 28 }: { size?: number }) {
  const tiles = [[0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 0], [1, 1, 1], [2, 1, 0], [0, 2, 0], [1, 2, 1], [2, 2, 0]]
  return (
    <svg width={size} height={size} viewBox="0 0 30 30" aria-hidden className="shrink-0">
      {tiles.map(([x, y, a], i) => <rect key={i} x={1 + x * 9.6} y={1 + y * 9.6} width={8.4} height={8.4} rx={2}
        className={a ? 'fill-accent' : 'fill-line'} />)}
    </svg>
  )
}
export default function Logo() {
  return <span className="flex items-center gap-2"><LogoMark /><span className="text-lg font-semibold tracking-tight">Tessera</span></span>
}
