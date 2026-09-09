import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // Bundle size analysis — run with: ANALYZE=true npm run build
    process.env.ANALYZE && visualizer({
      open: true,
      filename: 'dist/bundle-stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  // ── Vitest Configuration ────────────────────────────────
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: false,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/test/**', 'src/**/*.test.*', 'src/main.tsx', 'src/vite-env.d.ts'],
    },
  },

  // ── Build Optimization ─────────────────────────────────
  build: {
    // Target modern browsers for smaller output
    target: 'es2020',
    // Enable CSS minification
    cssMinify: true,
    // Warn on chunks larger than 300KB
    chunkSizeWarningLimit: 300,
    rollupOptions: {
      output: {
        // Split vendor code into separate cacheable chunks
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            // React core — rarely changes, cache aggressively
            if (id.includes('react-dom') || id.includes('react-router-dom') || id.includes('/react/')) {
              return 'react-vendor';
            }
            // Charting library — only needed on ResultsPage
            if (id.includes('chart.js') || id.includes('react-chartjs-2')) {
              return 'charts';
            }
            // Firebase client — auth
            if (id.includes('firebase')) {
              return 'firebase';
            }
            // UI libraries
            if (id.includes('framer-motion') || id.includes('lucide-react')) {
              return 'ui-vendor';
            }
            // Form + validation
            if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('/zod/')) {
              return 'form-vendor';
            }
            // State management + HTTP
            if (id.includes('zustand') || id.includes('axios')) {
              return 'state-vendor';
            }
          }
        },
      },
    },
    // Enable source maps for debugging (small overhead)
    sourcemap: false,
  },

  // ── Dev Optimization ───────────────────────────────────
  optimizeDeps: {
    // Pre-bundle heavy deps for faster dev cold starts
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand',
      'axios',
      'firebase/app',
      'firebase/auth',
      'lucide-react',
    ],
  },
})
