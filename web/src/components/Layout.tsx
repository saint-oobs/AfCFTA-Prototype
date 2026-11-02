import { NavLink, useLocation } from 'react-router-dom'
import { ReactNode, useEffect, useState } from 'react'
import Logo from './Logo'
import { Menu, Moon, Sun } from './icons'

const NAV = [['/', 'Overview'], ['/navigator', 'Navigator'], ['/monitoring', 'Monitoring'], ['/tests', 'Test log'], ['/logic', 'Show the logic'], ['/credits', 'Credits']] as const

function ThemeToggle() {
  const [dark, setDark] = useState<boolean>(() => {
    try { const t = localStorage.getItem('theme'); if (t === 'dark' || t === 'light') return t === 'dark' } catch { /* storage not available */ }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  useEffect(() => {
    const r = document.documentElement; r.classList.remove('dark', 'light'); r.classList.add(dark ? 'dark' : 'light')
  }, [dark])
  const toggle = () => { setDark(!dark); try { localStorage.setItem('theme', !dark ? 'dark' : 'light') } catch { /* storage not available */ } }
  return <button className="btn !p-2" onClick={toggle} aria-label={dark ? 'Change to light theme' : 'Change to dark theme'}>
    {dark ? <Sun /> : <Moon />}</button>
}

export default function Layout({ children }: { children: ReactNode }) {
  const loc = useLocation()
  const [open, setOpen] = useState(false)
  useEffect(() => { setOpen(false) }, [loc.pathname])
  return (
    <div className="min-h-screen flex flex-col">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:m-2 btn">Skip to content</a>
      <div role="note" className="bg-ink text-bg text-center text-xs py-1.5 no-print">Synthetic data – prototype – indicative only</div>
      <header className="sticky top-0 z-30 border-b border-line bg-bg/95 backdrop-blur no-print">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 h-14 flex items-center gap-4">
          <NavLink to="/" aria-label="Tessera home"><Logo /></NavLink>
          <nav aria-label="Main" className="hidden md:flex gap-1 ml-4">
            {NAV.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) =>
                `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${isActive ? 'bg-accent-soft text-accent' : 'text-muted hover:text-ink'}`}>{label}</NavLink>))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <ThemeToggle />
            <button className="btn md:hidden !p-2" aria-expanded={open} aria-label="Menu" onClick={() => setOpen(!open)}><Menu /></button>
          </div>
        </div>
        {open && <nav aria-label="Mobile" className="md:hidden border-t border-line px-4 py-2 flex flex-col">
          {NAV.map(([to, label]) => <NavLink key={to} to={to} className="py-2 text-sm">{label}</NavLink>)}</nav>}
      </header>
      <main id="main" className="flex-1">{children}</main>
      <footer className="border-t border-line mt-14 no-print">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-6 flex flex-wrap gap-4 justify-between items-center note">
          <Logo />
          <p className="max-w-xl">Prototype for the AI Adoption and Innovation Centre, Ghana. All firms and documents are synthetic. The result is indicative.</p>
        </div>
      </footer>
    </div>
  )
}
