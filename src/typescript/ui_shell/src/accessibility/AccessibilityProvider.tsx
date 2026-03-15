// GAIA Accessibility Provider.
//
// Owns:
//   - Preference persistence and session-start application (DSK-007)
//   - Reduced-motion context
//   - High-contrast context
//   - Keyboard traversal context
//   - Live region announcement helper
//
// Wrap the entire shell tree with <AccessibilityProvider> at the root.
// Components read preferences via useAccessibility().
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.5, §4.4

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';

export interface A11yPreferences {
  reducedMotion:  boolean;
  highContrast:   boolean;
  textScale:      number;   // 1.0 = default, 1.25 = large, 1.5 = x-large
  keyboardOnly:   boolean;
}

const STORAGE_KEY = 'gaia:a11y:preferences';

function loadPreferences(): A11yPreferences {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as A11yPreferences;
  } catch { /* ignore parse errors */ }
  // Defaults: honour OS reduced-motion preference (DSK-007)
  return {
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    highContrast:  window.matchMedia('(prefers-contrast: more)').matches,
    textScale:     1.0,
    keyboardOnly:  false,
  };
}

function persistPreferences(prefs: A11yPreferences): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch { /* storage unavailable */ }
}

interface A11yContextValue {
  preferences:    A11yPreferences;
  setPreferences: (next: Partial<A11yPreferences>) => void;
  announce:       (message: string, priority?: 'polite' | 'assertive') => void;
}

const A11yContext = createContext<A11yContextValue | null>(null);

export function useAccessibility(): A11yContextValue {
  const ctx = useContext(A11yContext);
  if (!ctx) throw new Error('useAccessibility must be used inside <AccessibilityProvider>');
  return ctx;
}

interface Props { children: ReactNode; }

export function AccessibilityProvider({ children }: Props): React.JSX.Element {
  const [preferences, setPrefs] = useState<A11yPreferences>(loadPreferences);
  const [announcement, setAnnouncement] = useState('');

  // Apply preferences to document root as CSS custom properties (DSK-007)
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--gaia-text-scale',    String(preferences.textScale));
    root.style.setProperty('--gaia-reduced-motion', preferences.reducedMotion ? '1' : '0');
    root.style.setProperty('--gaia-high-contrast',  preferences.highContrast  ? '1' : '0');
    persistPreferences(preferences);
  }, [preferences]);

  function setPreferences(next: Partial<A11yPreferences>): void {
    setPrefs(prev => ({ ...prev, ...next }));
  }

  function announce(message: string, _priority: 'polite' | 'assertive' = 'polite'): void {
    // Clear then set to ensure re-announcement of identical strings.
    setAnnouncement('');
    requestAnimationFrame(() => setAnnouncement(message));
  }

  return (
    <A11yContext.Provider value={{ preferences, setPreferences, announce }}>
      {children}

      {/* Visually hidden live region for announcements (DSK-003) */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        style={{
          position:   'absolute',
          width:      '1px',
          height:     '1px',
          padding:    '0',
          overflow:   'hidden',
          clip:       'rect(0,0,0,0)',
          whiteSpace: 'nowrap',
          border:     '0',
        }}
      >
        {announcement}
      </div>
    </A11yContext.Provider>
  );
}
