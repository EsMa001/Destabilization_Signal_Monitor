import { expect, test } from "@playwright/test";

// Traceability: AP-05, AP-09, AP-10
test.describe("API Mode Smoke", () => {
  test("loads overview with mock fallback disabled", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("topbar")).toBeVisible();
    await expect(page.getByTestId("mock-mode-chip")).toContainText(
      /mock fallback off/i,
    );
    await expect(page.getByTestId("backend-status-chip")).not.toContainText(
      /mock mode active/i,
    );
  });

  test("loads run builder without mock-mode hint", async ({ page }) => {
    await page.goto("/runs/new");

    await expect(page.getByTestId("topbar")).toBeVisible();
    await expect(page.getByTestId("mock-mode-chip")).toContainText(
      /mock fallback off/i,
    );
    await expect(page.getByTestId("run-builder-mock-mode")).toHaveCount(0);

    const optionsUnavailableCard = page.getByText(
      /run builder options unavailable/i,
    );
    const runBuilderForm = page.getByTestId("run-builder-form");
    const backendUnavailableCard = page.getByTestId(
      "run-builder-backend-unavailable",
    );

    await expect
      .poll(
        async () => {
          const counts = await Promise.all([
            runBuilderForm.count(),
            optionsUnavailableCard.count(),
            backendUnavailableCard.count(),
          ]);
          return counts[0] + counts[1] + counts[2];
        },
        { timeout: 15_000 },
      )
      .toBeGreaterThan(0);

    await expect(page.getByText(/mock run only/i)).toHaveCount(0);
  });
});
