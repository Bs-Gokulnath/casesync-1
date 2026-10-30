import Link from "next/link";
import { Button } from "@/components/ui/button";
import { serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { PageHeader } from "@/components/layout/PageHeader";
import { SearchForm } from "@/components/data-display/SearchForm";
import { ComplaintsTable } from "@/features/complaints/ComplaintsTable";
import { Plus } from "lucide-react";
import type { Bureau, Complaint, ComplaintCategory, Page } from "@/types/api";

export const metadata = { title: "Complaints — AICTE CaseWatch" };

const STATUS_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "received", label: "Received" },
  { value: "under_review", label: "Under review" },
  { value: "under_process", label: "Under process" },
  { value: "pending_information", label: "Pending information" },
  { value: "transferred", label: "Transferred" },
  { value: "escalated", label: "Escalated" },
  { value: "disposed", label: "Disposed" },
];

export default async function ComplaintsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string }>;
}) {
  const user = await requireSession();
  const canCreate = hasPermission(user, "complaint:create");

  const { q, status } = await searchParams;
  const query = new URLSearchParams();
  if (q) query.set("q", q);
  if (status) query.set("status", status);

  const [complaintsPage, bureaus, categories] = await Promise.all([
    serverApiFetch<Page<Complaint>>(`/complaints?${query.toString()}`),
    serverApiFetch<Bureau[]>("/reference/bureaus"),
    serverApiFetch<ComplaintCategory[]>("/reference/categories"),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Complaints"
        subtitle={`${complaintsPage.total} complaint${complaintsPage.total === 1 ? "" : "s"}`}
        action={
          canCreate && (
            <Button asChild className="glow-primary">
              <Link href="/complaints/new">
                <Plus className="size-4" />
                New Complaint
              </Link>
            </Button>
          )
        }
      />

      <SearchForm
        action="/complaints"
        defaultValue={q}
        placeholder="Search by subject or case ref..."
      >
        <select
          name="status"
          defaultValue={status ?? ""}
          className="border-input bg-input/40 focus:ring-ring/50 h-9 rounded-full border px-3 text-sm text-white outline-none focus:ring-2 [&>option]:bg-[#0c0e19]"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </SearchForm>

      <ComplaintsTable
        complaints={complaintsPage.items}
        bureaus={bureaus}
        categories={categories}
      />
    </div>
  );
}
