import { test, expect, type Page } from "@playwright/test";
import { loginAs } from "./helpers";

function statusBadge(page: Page, text: string) {
  return page.locator('[data-slot="badge"]').filter({ hasText: text });
}

// Exercises three of the five flows the brief calls out in one continuous
// case lifecycle: create complaint -> transfer -> disposal.
test("create, transfer, and dispose a complaint", async ({ page }) => {
  await loginAs(page, "rb.officer@aictecasewatch-demo.org");

  await page.goto("/complaints/new");
  await page.getByRole("combobox", { name: "Institution" }).click();
  await page.getByRole("option", { name: /Delta Institute of Technology/ }).click();

  await page.getByRole("combobox", { name: "Category" }).click();
  await page.getByRole("option", { name: /Fee Refund/ }).click();

  const subject = `E2E transfer-and-dispose test ${Date.now()}`;
  await page.getByLabel("Subject").fill(subject);
  await page
    .getByLabel("Description")
    .fill("End-to-end test complaint covering transfer and disposal.");
  await page.getByRole("button", { name: "Register complaint" }).click();

  await page.waitForURL(/\/complaints\/\d+$/);
  await expect(page.getByRole("heading", { name: subject })).toBeVisible();
  await expect(statusBadge(page, "Received")).toBeVisible();

  // Received -> Under review
  await page.getByRole("button", { name: "Start Review" }).click();
  const reviewDialog = page.getByRole("dialog");
  await reviewDialog.getByRole("button", { name: "Confirm" }).click();
  await expect(statusBadge(page, "Under Review")).toBeVisible();

  // Transfer to PGRC
  await page.getByRole("button", { name: "Transfer", exact: true }).click();
  const transferDialog = page.getByRole("dialog");
  await transferDialog.getByRole("combobox", { name: "Target bureau" }).click();
  await page.getByRole("option", { name: "Public Grievance Redressal Cell" }).click();
  await transferDialog
    .getByLabel("Reason")
    .fill("Jurisdiction belongs to PGRC for this complaint type.");
  await transferDialog.getByRole("button", { name: "Transfer", exact: true }).click();
  await expect(statusBadge(page, "Transferred")).toBeVisible();

  // Transferred -> Under review again (new bureau acknowledges)
  await page.getByRole("button", { name: "Acknowledge & Review" }).click();
  const ackDialog = page.getByRole("dialog");
  await ackDialog.getByRole("button", { name: "Confirm" }).click();
  await expect(statusBadge(page, "Under Review")).toBeVisible();

  // Dispose
  await page.getByRole("button", { name: "Dispose" }).click();
  const disposeDialog = page.getByRole("dialog");
  await disposeDialog
    .getByLabel("Disposal note")
    .fill("Issue resolved; refund processed by the institute.");
  await disposeDialog.getByRole("button", { name: "Confirm disposal" }).click();
  await expect(statusBadge(page, "Disposed")).toBeVisible();
  await expect(page.getByText("Issue resolved; refund processed by the institute.")).toBeVisible();
});
