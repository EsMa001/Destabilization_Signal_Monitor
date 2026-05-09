import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Traceability: AP-05, AP-07, AP-08
const ENV_KEYS = [
  "NEXT_PUBLIC_ENABLE_MOCK_FALLBACK",
  "NEXT_PUBLIC_API_FALLBACK_MODE",
  "NEXT_PUBLIC_API_BASE_URL",
] as const;

const ORIGINAL_ENV = new Map<string, string | undefined>(ENV_KEYS.map((key) => [key, process.env[key]]));

function restoreEnv(): void {
  for (const key of ENV_KEYS) {
    const value = ORIGINAL_ENV.get(key);
    if (typeof value === "undefined") {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
}

async function loadClient(mockFallbackEnabled: "true" | "false") {
  process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK = mockFallbackEnabled;
  process.env.NEXT_PUBLIC_API_FALLBACK_MODE = "off";
  process.env.NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000/api/v1";
  vi.resetModules();
  return import("@/lib/api/client");
}

describe("apiClient fallback separation", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    restoreEnv();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("does not return fake runs when mock fallback is disabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("network down")),
    );
    const { apiClient, BackendUnavailableError } = await loadClient("false");

    await expect(
      apiClient.createRun({
        countries: ["Germany", "Iran"],
        horizon_days: 30,
        layers: ["event", "governance"],
      }),
    ).rejects.toBeInstanceOf(BackendUnavailableError);
  });

  it("returns explicit mock runs when mock fallback is enabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("network down")),
    );
    const { apiClient } = await loadClient("true");

    const result = await apiClient.createRun({
      countries: ["Germany", "Iran"],
      horizon_days: 30,
      layers: ["event", "governance"],
    });

    expect(result.source).toBe("mock");
    expect(result.run_id).toMatch(/^mock_run_/);
  });

  it("reports backend state as unavailable when mock fallback is disabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("health unreachable")),
    );
    const { apiClient } = await loadClient("false");

    const status = await apiClient.getBackendConnectivity();

    expect(status.state).toBe("unavailable");
    expect(status.mock_fallback_enabled).toBe(false);
  });

  it("reports backend state as mock mode when mock fallback is enabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("health unreachable")),
    );
    const { apiClient } = await loadClient("true");

    const status = await apiClient.getBackendConnectivity();

    expect(status.state).toBe("mock_mode");
    expect(status.mock_fallback_enabled).toBe(true);
  });
});
