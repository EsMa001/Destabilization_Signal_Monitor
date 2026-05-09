import { expect, test } from "@playwright/test";

// Traceability: AP-09, AP-10
test.describe("Mock Mode Smoke", () => {
  test("loads overview route", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("overview-map")).toBeVisible();
    await expect(page.getByTestId("backend-status-chip")).toContainText(/mock mode active/i);
  });

  test("loads runs route", async ({ page }) => {
    await page.goto("/runs");
    await expect(page.getByTestId("run-monitor-panel")).toBeVisible();
    await expect(page.getByTestId("run-monitor-table")).toBeVisible();
  });

  test("loads run builder route", async ({ page }) => {
    await page.goto("/runs/new");
    await expect(page.getByTestId("run-builder-form")).toBeVisible();
    await expect(page.getByTestId("run-builder-mock-mode")).toBeVisible();
  });

  test("loads country detail route", async ({ page }) => {
    await page.goto("/countries/Germany");
    await expect(page.getByTestId("country-mode-toggle")).toBeVisible();
  });

  test("loads compare route", async ({ page }) => {
    await page.goto("/compare");
    await expect(page.getByTestId("compare-selection-panel")).toBeVisible();
  });

  test("loads coverage route", async ({ page }) => {
    await page.goto("/coverage");
    await expect(page.getByTestId("coverage-matrix-panel")).toBeVisible();
    await expect(page.getByTestId("coverage-table")).toBeVisible();
  });

  test("loads artifacts route", async ({ page }) => {
    await page.goto("/artifacts");
    await expect(page.getByTestId("artifacts-by-run-panel")).toBeVisible();
    await expect(page.getByTestId("artifact-list")).toBeVisible();
  });

  test("sidebar navigation works across key routes", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("nav-link-runs").click();
    await expect(page).toHaveURL(/\/runs$/);
    await page.getByTestId("nav-link-countries").click();
    await expect(page).toHaveURL(/\/countries$/);
    await page.getByTestId("nav-link-compare").click();
    await expect(page).toHaveURL(/\/compare$/);
  });
});
