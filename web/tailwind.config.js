/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: Object.fromEntries(['bg', 'panel', 'surface', 'ink', 'muted', 'line', 'accent', 'accent-soft', 'crit', 'major', 'minor', 'ok', 's1', 's2']
        .map(k => [k, `rgb(var(--${k}) / <alpha-value>)`])),
      fontFamily: { sans: ['"Public Sans Variable"', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
}
