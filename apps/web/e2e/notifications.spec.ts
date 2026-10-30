import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test("assigning a case notifies the officer, who can mark it read", async ({ page }) => {
  await loginAs(page, "rb.officer@aictecasewatch-demo.org");

  // Create a complaint and self-assign it, which raises an ASSIGNMENT notification.
  await page.goto("/complaints/new");
  await page.getByRole("combobox", { name: "Institution" }).click();
  await page.getByRole("option").first().click();
  await page.getByRole("combobox", { name: "Category" }).click();
  await page.getByRole("option").first().click();
  const subject = `E2E notification test ${Date.now()}`;
  await page.getByLabel("Subject").fill(subject);
  await page
    .getByLabel("Description")
    .fill("A complaint created to trigger an assignment notification.");
  await page.getByRole("button", { name: "Register complaint" }).click();
  await page.waitForURL(/\/complaints\/\d+$/);

  await page.getByRole("button", { name: "Assign" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("combobox", { name: "Officer" }).click();
  await page.getByRole("option", { name: /Regional Bureau Officer \(Delhi\)/ }).click();
  await dialog.getByRole("button", { name: "Assign", exact: true }).click();
  await expect(page.getByText("Officer assigned")).toBeVisible();

  await page.goto("/notifications");
  const notification = page.locator("li").filter({ hasText: subject }).first();
  await expect(notification).toBeVisible();
  await expect(notification.getByText("Mark read")).toBeVisible();

  await notification.getByRole("button", { name: "Mark read" }).click();
  await expect(notification.getByRole("button", { name: "Mark read" })).toHaveCount(0);
});
