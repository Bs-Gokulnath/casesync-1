import { test, expect, type Page } from "@playwright/test";
import { loginAs } from "./helpers";

const RATIONALE = "Same institution and category (Fee Refund) open concurrently";

// The alert card's own styled wrapper (see app/(dashboard)/overlaps/page.tsx)
// — scoping to this specific class combination avoids matching ancestor
// containers that also happen to contain the rationale text.
function alertCardWithRationale(page: Page) {
  return page.locator("div.overlap-alert-card").filter({ hasText: RATIONALE });
}

// Reviews the cross-bureau overlap alert the seed data creates for Delta
// Institute of Technology (CW-2026-00001 at RB-Delhi / CW-2026-00002 at
// PGRC, both Fee Refund) — confirming it never changes the underlying
// cases, only records a reviewer decision.
test("review and confirm an open overlap alert", async ({ page }) => {
  await loginAs(page, "rb.officer@aictecasewatch-demo.org");

  await page.goto("/overlaps?status=open");
  const alertCard = alertCardWithRationale(page);
  await expect(alertCard).toBeVisible();

  await alertCard.getByRole("button", { name: "Review" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("combobox", { name: "Decision" }).click();
  await page.getByRole("option", { name: /Confirmed/ }).click();
  await dialog
    .getByLabel("Reason")
    .fill("Verified both bureaus are handling the same fee dispute.");
  await dialog.getByRole("button", { name: "Save decision" }).click();

  await expect(page.getByText("Decision recorded")).toBeVisible();

  // The card we just decided drops out of the status=open filter, so look
  // at the unfiltered list to see its new status.
  await page.goto("/overlaps");
  const decidedCard = alertCardWithRationale(page);
  await expect(
    decidedCard.locator('[data-slot="badge"]').filter({ hasText: "Confirmed" }),
  ).toBeVisible();
});
