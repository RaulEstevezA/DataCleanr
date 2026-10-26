import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  // Production build is served from the portfolio at raulesteveza.github.io/tools/DataCleanr/
  base: command === 'build' ? '/tools/DataCleanr/' : '/',
}))
