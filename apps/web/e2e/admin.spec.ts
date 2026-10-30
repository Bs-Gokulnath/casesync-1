import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test("system admin can create a bureau and a user from Settings", async ({ page }) => {
  await loginAs(page, "admin@aictecasewatch-demo.org");
  await page.goto("/settings");

  // Bureaus tab is active by default
  const code = `E2E${Date.now() % 100000}`;
  await page.getByLabel("Code").fill(code);
  await page.getByLabel("Name", { exact: true }).fill("E2E Test Bureau");
  await page.getByRole("button", { name: "Add" }).click();
  await expect(page.getByText("Bureau created")).toBeVisible();
  await expect(page.getByRole("cell", { name: code })).toBeVisible();

  // Users tab
  await page.getByRole("tab", { name: "Users" }).click();
  await page.getByRole("button", { name: "New user" }).click();

  const dialog = page.getByRole("dialog");
  const email = `e2e.user.${Date.now()}@aictecasewatch-demo.org`;
  await dialog.getByLabel("Employee code").fill(`EMP-${Date.now() % 100000}`);
  await dialog.getByLabel("Full name").fill("E2E Test User");
  await dialog.getByLabel("Email").fill(email);
  await dialog.getByLabel("Temporary password").fill("Correct-Horse-1");
  await dialog.getByRole("button", { name: "Create" }).click();

  await expect(page.getByText("User created")).toBeVisible();
  await expect(page.getByText(email)).toBeVisible();
});

test("a non-admin is redirected away from Settings", async ({ page }) => {
  await loginAs(page, "rb.officer@aictecasewatch-demo.org");
  await page.goto("/settings");
  await expect(page).toHaveURL(/\/overview$/);
});
