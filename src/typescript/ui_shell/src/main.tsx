// GAIA UI Shell — React 19 entry point.
//
// Mounts two independent React roots:
//   #gaia-hud-root    — Consciousness HUD (floating, aria-live, fixed top band)
//   #gaia-shell-root  — Primary operator shell
//
// The two roots are intentionally separate so HUD updates never cause
// the shell tree to re-render, and the shell can be replaced without
// touching the HUD mount (DSK-002: shell is a replaceable layer).
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.3, §2.4

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { ConsciousnessHUD } from './hud/ConsciousnessHUD';
import { sampleCoreStatuses } from './hud/coreStatuses';

// --- Mount HUD ---
const hudEl = document.getElementById('gaia-hud-root');
if (!hudEl) throw new Error('[GAIA] #gaia-hud-root not found in DOM');
createRoot(hudEl).render(
  <StrictMode>
    <ConsciousnessHUD statuses={sampleCoreStatuses} />
  </StrictMode>,
);

// --- Mount shell ---
const shellEl = document.getElementById('gaia-shell-root');
if (!shellEl) throw new Error('[GAIA] #gaia-shell-root not found in DOM');
createRoot(shellEl).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
