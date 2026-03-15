// GAIA UI Shell — root application component.
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.3, §2.5
//
// Tree:
//   AccessibilityProvider  — preference persistence, reduced-motion, high-contrast,
//                             keyboard traversal, live region announcements (DSK-003/007)
//     GaiaShell            — panels, workspace switcher, launch surface (DSK-002)

import { AccessibilityProvider } from './accessibility/AccessibilityProvider';
import { GaiaShell } from './shell/GaiaShell';
import { initialShellState } from './state/store';

export default function App(): React.JSX.Element {
  return (
    <AccessibilityProvider>
      <GaiaShell state={initialShellState} />
    </AccessibilityProvider>
  );
}
