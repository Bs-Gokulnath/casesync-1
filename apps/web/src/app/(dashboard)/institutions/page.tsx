import { serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { PageHeader } from "@/components/layout/PageHeader";
import { SearchForm } from "@/components/data-display/SearchForm";
import { InstitutionsTable } from "@/features/institutions/InstitutionsTable";
import { InstitutionFormDialog } from "@/features/institutions/InstitutionFormDialog";
import type { Page, Institution, Region } from "@/types/api";

export const metadata = { title: "Institutions — AICTE CaseWatch" };

export default async function InstitutionsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const user = await requireSession();
  const canCreate = hasPermission(user, "institution:write");

  const { q } = await searchParams;
  const query = new URLSearchParams();
  if (q) query.set("q", q);

  const [institutionsPage, regions] = await Promise.all([
    serverApiFetch<Page<Institution>>(`/institutions?${query.toString()}`),
    serverApiFetch<Region[]>("/reference/regions"),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Institutions"
        subtitle={`${institutionsPage.total} institution${institutionsPage.total === 1 ? "" : "s"}`}
        action={canCreate && <InstitutionFormDialog regions={regions} />}
      />

      <SearchForm action="/institutions" defaultValue={q} placeholder="Search by name..." />

      <InstitutionsTable institutions={institutionsPage.items} regions={regions} />
    </div>
  );
}
