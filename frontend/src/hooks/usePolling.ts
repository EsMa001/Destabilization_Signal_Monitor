"use client";

import { useEffect } from "react";

export function usePolling(callback: () => void, intervalMs: number, enabled = true): void {
  useEffect(() => {
    if (!enabled) {
      return;
    }

    callback();
    const id = window.setInterval(callback, intervalMs);
    return () => window.clearInterval(id);
  }, [callback, intervalMs, enabled]);
}
