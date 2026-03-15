import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

// GAIA UI Shell — Vite 6 configuration
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.3
//
// Path aliases MUST mirror tsconfig.json "paths" exactly.
// If you add an alias here, add the matching entry to tsconfig.json too.

export default defineConfig({
  plugins: [react()],

  // --- Dev server ---
  server: {
    port:        4173,
    strictPort:  true,   // fail fast if port is occupied
    host:        '127.0.0.1', // loopback only; do not expose to LAN in dev
  },

  // --- Preview server (vite preview) ---
  preview: {
    port:       4173,
    strictPort: true,
    host:       '127.0.0.1',
  },

  // --- Path aliases (mirrors tsconfig.json "paths") ---
  resolve: {
    alias: {
      '@shell': resolve(__dirname, 'src/shell'),
      '@hud':   resolve(__dirname, 'src/hud'),
      '@a11y':  resolve(__dirname, 'src/accessibility'),
      '@ipc':   resolve(__dirname, 'src/ipc'),
      '@types': resolve(__dirname, 'src/types'),
    },
  },

  // --- Build ---
  build: {
    target:     'es2020',
    sourcemap:  true,
    outDir:     'dist',
    // Warn if any individual chunk exceeds 500 kB (default 500 kB).
    // The HUD update loop must not ship a bloated bundle that delays first paint.
    chunkSizeWarningLimit: 500,
  },

  // --- Vitest inline config ---
  // Keeps test config co-located with build config; no separate vitest.config.ts needed.
  test: {
    globals:     true,
    environment: 'jsdom',
    setupFiles:  ['src/test-setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
    },
  },
});
