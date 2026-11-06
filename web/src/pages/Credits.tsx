import { PageHead, Section } from '../components/ui'

const ROWS = [
  ['React 18.3.1', 'UI library', 'MIT', 'https://react.dev'],
  ['React Router 6.28', 'Hash routing for GitHub Pages', 'MIT', 'https://reactrouter.com'],
  ['Vite 5.4', 'Build tool', 'MIT', 'https://vitejs.dev'],
  ['Tailwind CSS 3.4', 'Styling', 'MIT', 'https://tailwindcss.com'],
  ['anime.js 3.2.2', 'Stage transitions, result reveal, landing counters', 'MIT', 'https://animejs.com'],
  ['Pyodide 0.26.4 (CDN)', 'Runs the Python engine in the browser', 'MPL-2.0', 'https://pyodide.org'],
  ['Public Sans (Fontsource)', 'Typeface', 'SIL OFL 1.1', 'https://fontsource.org/fonts/public-sans'],
  ['Caveat (Fontsource)', 'Handwriting-style font for synthetic document images', 'SIL OFL 1.1', 'https://fontsource.org/fonts/caveat'],
  ['Laws.Africa – AfCFTA Agreement text', 'Source of Annex 2 rule text', 'CC-BY', 'https://laws.africa'],
]
export default function Credits() {
  return (
    <>
      <PageHead title="Credits" />
      <div className="mx-auto max-w-7xl px-4 sm:px-6 space-y-6">
        <Section title="Libraries, fonts and sources"><div className="overflow-x-auto"><table className="data text-sm">
          <thead><tr><th>Item</th><th>Used for</th><th>Licence</th><th>Link</th></tr></thead>
          <tbody>{ROWS.map(r => <tr key={r[0]}><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td><a className="text-accent hover:underline break-all" href={r[3]} target="_blank" rel="noreferrer">{r[3]}</a></td></tr>)}</tbody></table></div></Section>
        <Section title="Generative AI"><p className="text-sm max-w-3xl">The code, the rule extraction, the synthetic data and draft documents of this prototype were produced with Claude (Anthropic), a generative AI assistant, under the group’s direction.</p></Section>
      </div>
    </>
  )
}
