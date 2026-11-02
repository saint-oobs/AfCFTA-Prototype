// One SVG icon set used on every screen (no emoji or font glyphs, so icons look the same on all devices).
import { SVGProps } from 'react'
type P = SVGProps<SVGSVGElement> & { size?: number }
const base = (size = 16, p: P) => ({ width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2,
  strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, 'aria-hidden': true, ...p })
export const Check = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M20 6 9 17l-5-5" /></svg>
export const X = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M18 6 6 18M6 6l12 12" /></svg>
export const Help = ({ size, ...p }: P) => <svg {...base(size, p)}><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17h.01" /></svg>
export const Alert = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M12 3 2 20h20L12 3z" /><path d="M12 10v4M12 17h.01" /></svg>
export const Octagon = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M8 2h8l6 6v8l-6 6H8l-6-6V8z" /><path d="M12 8v4M12 16h.01" /></svg>
export const Info = ({ size, ...p }: P) => <svg {...base(size, p)}><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></svg>
export const ArrowRight = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
export const ArrowLeft = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M19 12H5M11 6l-6 6 6 6" /></svg>
export const Sun = ({ size, ...p }: P) => <svg {...base(size, p)}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
export const Moon = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></svg>
export const Upload = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M12 15V3M7 8l5-5 5 5M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4" /></svg>
export const FileText = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6M8 13h8M8 17h6" /></svg>
export const Scan = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10" /></svg>
export const Cpu = ({ size, ...p }: P) => <svg {...base(size, p)}><rect x="5" y="5" width="14" height="14" rx="2" /><path d="M9 9h6v6H9zM9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3" /></svg>
export const Scale = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M12 3v18M5 21h14M6 7h12M6 7l-3 7a3 3 0 0 0 6 0zM18 7l-3 7a3 3 0 0 0 6 0z" /></svg>
export const User = ({ size, ...p }: P) => <svg {...base(size, p)}><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>
export const Activity = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
export const Search = ({ size, ...p }: P) => <svg {...base(size, p)}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
export const Tag = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z" /><path d="M7.5 7.5h.01" /></svg>
export const Book = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z" /><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5" /></svg>
export const Message = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
export const Printer = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6z" /></svg>
export const Copy = ({ size, ...p }: P) => <svg {...base(size, p)}><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
export const Refresh = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M21 12a9 9 0 1 1-3-6.7L21 8M21 3v5h-5" /></svg>
export const Send = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="m22 2-7 20-4-9-9-4zM22 2 11 13" /></svg>
export const Menu = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M3 6h18M3 12h18M3 18h18" /></svg>
export const Download = ({ size, ...p }: P) => <svg {...base(size, p)}><path d="M12 3v12M7 10l5 5 5-5M4 19h16" /></svg>
