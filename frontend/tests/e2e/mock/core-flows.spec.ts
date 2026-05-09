import { expect, test } from "@playwright/test";

// Traceability: AP-10
test.describe("Mock Mode Core Flows", () => {
  test("navigates from overview map to country detail", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("map-country-germany").click();
    await expect(page).toHaveURL(/\/countries\/(Germany|DEU)/i);
    await expect(page.getByTestId("country-mode-toggle")).toBeVisible();
  });

  test("submits run builder in explicit mock mode", async ({ page }) => {
    await page.goto("/runs/new");
    await expect(page.getByTestId("run-builder-mock-mode")).toBeVisible();

    await page.getByTestId("run-builder-submit").click();

    await expect(page.getByTestId("run-builder-submit-success")).toContainText(/run created:/i);
    await expect(page.getByTestId("run-builder-submit-success")).toContainText(/mock run only/i);
  });

  test("updates compare selection with clear/top3 controls", async ({ page }) => {
    await page.goto("/compare");
    await expect(page.getByTestId("compare-selection-panel")).toBeVisible();

    await page.getByTestId("compare-clear-button").click();
    await expect(page.getByText(/select at least two countries/i)).toBeVisible();

    await page.getByTestId("compare-top3-button").click();
    await expect(page.locator('input[type="checkbox"]:checked')).toHaveCount(3);
  });

  test("opens country detail from coverage table", async ({ page }) => {
    await page.goto("/coverage");
    await expect(page.getByTestId("coverage-table")).toBeVisible();
    await page.getByRole("button", { name: "Open" }).first().click();
    await expect(page).toHaveURL(/\/countries\//i);
    await expect(page.getByTestId("country-mode-toggle")).toBeVisible();
  });
});
