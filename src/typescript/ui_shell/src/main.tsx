// GAIA UI Shell — React 19 entry point.
//
// Single root mount: <App /> at #root.
// The Consciousness HUD is rendered inside App via a React portal
// into #gaia-hud-portal so it stays in the same React tree
// (shared context, shared error boundary) while remaining visually
// fixed above the shell layer in the DOM.
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.3, §2.4

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('[GAIA] #root mount element not found in DOM');

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
