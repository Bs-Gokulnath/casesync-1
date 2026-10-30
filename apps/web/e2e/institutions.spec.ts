import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test("create an institution and view its detail page", async ({ page }) => {
  await loginAs(page, "admin@aictecasewatch-demo.org");

  await page.goto("/institutions");
  await page.getByRole("button", { name: "New Institution" }).click();

  const dialog = page.getByRole("dialog");
  const name = `E2E Institute ${Date.now()}`;
  await dialog.getByLabel("Institution name").fill(name);
  await dialog.getByRole("combobox").click();
  await page.getByRole("option").first().click();
  await dialog.getByRole("button", { name: "Create institution" }).click();

  await expect(page.getByText("Institution created")).toBeVisible();
  await expect(page.getByRole("link", { name })).toBeVisible();

  await page.getByRole("link", { name }).click();
  await page.waitForURL(/\/institutions\/\d+$/);
  await expect(page.getByRole("heading", { name })).toBeVisible();
  await expect(page.getByText("Total complaints")).toBeVisible();

  // Deactivate / reactivate via the status toggle
  await page.getByRole("button", { name: "Deactivate" }).click();
  const statusDialog = page.getByRole("dialog");
  await statusDialog.getByLabel("Reason").fill("E2E test deactivation");
  await statusDialog.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByText("Institution deactivated")).toBeVisible();
  await expect(page.locator('[data-slot="badge"]').filter({ hasText: "Inactive" })).toBeVisible();

  await page.getByRole("button", { name: "Activate" }).click();
  const reactivateDialog = page.getByRole("dialog");
  await reactivateDialog.getByLabel("Reason").fill("E2E test reactivation");
  await reactivateDialog.getByRole("button", { name: "Confirm" }).click();
  await expect(page.getByText("Institution activated")).toBeVisible();
});

test("auditor does not see the New Institution button", async ({ page }) => {
  await loginAs(page, "auditor@aictecasewatch-demo.org");
  await page.goto("/institutions");
  await expect(page.getByRole("button", { name: "New Institution" })).toHaveCount(0);
});
