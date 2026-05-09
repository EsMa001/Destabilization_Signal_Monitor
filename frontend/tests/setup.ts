import { createElement } from "react";
import type { ReactNode } from "react";
import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

if (typeof process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK === "undefined") {
  process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK = "false";
}
if (typeof process.env.NEXT_PUBLIC_API_FALLBACK_MODE === "undefined") {
  process.env.NEXT_PUBLIC_API_FALLBACK_MODE = "off";
}

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string | { pathname?: string };
    children: ReactNode;
  }) =>
    createElement(
      "a",
      {
        href: typeof href === "string" ? href : href.pathname ?? "#",
        ...props,
      },
      children,
    ),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
