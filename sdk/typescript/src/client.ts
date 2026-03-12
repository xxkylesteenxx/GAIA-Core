/**
 * GAIA TypeScript SDK — GAPI Client
 *
 * Layer: L6 — Apps / SDK / Scripting / Plugins
 * Language: TypeScript
 *
 * Thin typed client for the GAIA Platform API (GAPI).
 * Use this in web-tech apps (Electron, Next.js dashboards, portal UIs).
 */

export interface GaiaInferRequest {
  prompt: string;
  max_tokens?: number;
}

export interface GaiaInferResponse {
  text: string;
  tokens_used: number;
  model: string;
}

export interface AtlasQueryRequest {
  domain: 'AERO' | 'TERRA' | 'AQUA' | 'VITA' | 'GENERAL';
  query_type: 'SUMMARY' | 'CURRENT_CONDITIONS' | 'CONTEXT_FOR_LOCATION';
  location?: { lat: number; lon: number };
}

export class GaiaClient {
  constructor(
    private readonly baseUrl: string = 'http://localhost:8080',
    private readonly apiKey?: string,
  ) {}

  private get headers(): HeadersInit {
    return this.apiKey
      ? { 'Content-Type': 'application/json', Authorization: `Bearer ${this.apiKey}` }
      : { 'Content-Type': 'application/json' };
  }

  async healthz(): Promise<Record<string, string>> {
    const res = await fetch(`${this.baseUrl}/healthz`, { headers: this.headers });
    if (!res.ok) throw new Error(`healthz failed: ${res.status}`);
    return res.json();
  }

  async infer(req: GaiaInferRequest): Promise<GaiaInferResponse> {
    const res = await fetch(`${this.baseUrl}/v1/infer`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`infer failed: ${res.status}`);
    return res.json();
  }

  async atlasQuery(req: AtlasQueryRequest): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.baseUrl}/v1/atlas/query`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`atlas query failed: ${res.status}`);
    return res.json();
  }
}
