import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// base './' keeps asset URLs relative: the build works under the shell's backend and on GitHub Pages.
export default defineConfig({
  base: './',
  plugins: [react()],
  build: { outDir: 'frontend/dist', emptyOutDir: true },
})
