import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("rejects an invalid password with a visible error", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("admin@aictecasewatch-demo.org");
    await page.getByLabel("Password").fill("wrong-password");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByText("Incorrect email or password.")).toBeVisible();
    await expect(page).toHaveURL(/\/login$/);
  });

  test("signs in and reaches the overview dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("admin@aictecasewatch-demo.org");
    await page.getByLabel("Password").fill("Demo@12345");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(/\/overview$/);
    await expect(page.getByRole("heading", { name: /Welcome,/ })).toBeVisible();
  });

  test("an unauthenticated visitor is redirected away from the dashboard", async ({ page }) => {
    await page.goto("/overview");
    await expect(page).toHaveURL(/\/login$/);
  });
});
