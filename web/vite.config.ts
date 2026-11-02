import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Relative base + hash routing: works on GitHub Pages under any repo name and inside an iframe.
export default defineConfig({
  base: './',
  plugins: [react()],
  worker: { format: 'iife' },
  build: { outDir: 'dist', chunkSizeWarningLimit: 900 },
})
