import { redirect } from "next/navigation";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { serverApiFetch } from "@/lib/api/server-client";
import { PageHeader } from "@/components/layout/PageHeader";
import { CreateComplaintForm } from "@/features/complaints/CreateComplaintForm";
import type { Bureau, ComplaintCategory, Institution, Page } from "@/types/api";

export const metadata = { title: "New Complaint — AICTE CaseWatch" };

export default async function NewComplaintPage() {
  const user = await requireSession();
  if (!hasPermission(user, "complaint:create")) {
    redirect("/complaints");
  }

  const [institutionsPage, categories, bureaus] = await Promise.all([
    serverApiFetch<Page<Institution>>("/institutions?page_size=100"),
    serverApiFetch<ComplaintCategory[]>("/reference/categories"),
    serverApiFetch<Bureau[]>("/reference/bureaus"),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Register a complaint"
        subtitle={
          user.role === "bureau_officer"
            ? "This will be registered against your bureau."
            : "Choose the institution and the bureau that will handle this case."
        }
      />

      <CreateComplaintForm
        institutions={institutionsPage.items}
        categories={categories}
        bureaus={bureaus}
        showBureauSelect={user.role !== "bureau_officer"}
      />
    </div>
  );
}
