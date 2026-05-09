import { expect, test } from "@playwright/test";

// Traceability: AP-05, AP-10
test.describe("API Mode Separation", () => {
  test("blocks fake run creation when backend is unavailable and mock fallback is disabled", async ({ page }) => {
    await page.goto("/runs/new");

    const backendUnavailableCard = page.getByTestId("run-builder-backend-unavailable");
    const optionsUnavailableCard = page.getByText(/run builder options unavailable/i);
    const hasBackendUnavailableCard = await backendUnavailableCard
      .isVisible()
      .catch(() => false);

    if (!hasBackendUnavailableCard) {
      await expect(optionsUnavailableCard).toBeVisible();
    }

    const submitButton = page.getByTestId("run-builder-submit");
    if ((await submitButton.count()) > 0) {
      await expect(submitButton).toBeDisabled();
    }

    await expect(page.getByText(/run created:/i)).toHaveCount(0);
    await expect(page.getByTestId("backend-status-chip")).toContainText(/backend unavailable/i);
    await expect(page.getByTestId("mock-mode-chip")).toContainText(/mock fallback off/i);
  });
});
