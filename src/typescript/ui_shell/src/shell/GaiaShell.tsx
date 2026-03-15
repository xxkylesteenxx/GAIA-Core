// GAIA Shell — primary operator surface.
//
// Owns: panels, workspace switcher, launch surface, notifications.
// Treated as a replaceable presentation layer above the IPC contract (DSK-002).
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.3

import type { ShellState } from '../state/store';

interface GaiaShellProps {
  state: ShellState;
}

export function GaiaShell({ state }: GaiaShellProps): React.JSX.Element {
  return (
    <div
      role="region"
      aria-label="GAIA Shell"
      style={{
        display:       'flex',
        flexDirection: 'column',
        height:        '100%',
        padding:       '8px 16px',
      }}
    >
      {/* Workspace indicator */}
      <nav aria-label="Workspaces">
        {Array.from({ length: state.workspaceCount }, (_, i) => (
          <button
            key={i}
            aria-pressed={i === state.activeWorkspace}
            aria-label={`Workspace ${i + 1}${
              i === state.activeWorkspace ? ' (active)' : ''
            }`}
            style={{
              marginRight: '8px',
              fontWeight:  i === state.activeWorkspace ? 'bold' : 'normal',
            }}
          >
            {i + 1}
          </button>
        ))}
      </nav>

      {/* Surface list */}
      <main aria-label="Open surfaces" style={{ marginTop: '16px' }}>
        {state.surfaces.length === 0 ? (
          <p style={{ opacity: 0.5 }}>No surfaces open.</p>
        ) : (
          <ul role="list">
            {state.surfaces
              .filter(s => s.workspace === state.activeWorkspace)
              .map(s => (
                <li
                  key={s.id}
                  aria-current={s.focused ? 'true' : undefined}
                  style={{ fontWeight: s.focused ? 'bold' : 'normal' }}
                >
                  {s.title}
                </li>
              ))}
          </ul>
        )}
      </main>
    </div>
  );
}
