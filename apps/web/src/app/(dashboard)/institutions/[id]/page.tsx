import { notFound } from "next/navigation";
import { ApiError, serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { ComplaintsTable } from "@/features/complaints/ComplaintsTable";
import { InstitutionStatusToggle } from "@/features/institutions/InstitutionStatusToggle";
import { StatCard } from "@/components/data-display/StatCard";
import { Badge } from "@/components/ui/badge";
import type {
  Bureau,
  Complaint,
  ComplaintCategory,
  InstitutionDetail,
  Page,
  Region,
} from "@/types/api";

export const metadata = { title: "Institution — AICTE CaseWatch" };

export default async function InstitutionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = await requireSession();
  const canChangeStatus = hasPermission(user, "institution:status");

  let institution: InstitutionDetail;
  try {
    institution = await serverApiFetch<InstitutionDetail>(`/institutions/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const [regions, bureaus, categories, complaintsPage] = await Promise.all([
    serverApiFetch<Region[]>("/reference/regions"),
    serverApiFetch<Bureau[]>("/reference/bureaus"),
    serverApiFetch<ComplaintCategory[]>("/reference/categories"),
    serverApiFetch<Page<Complaint>>(`/complaints?institution_id=${id}&page_size=50`),
  ]);

  const region = regions.find((r) => r.id === institution.region_id);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-[#9b8dff]">{institution.institution_code}</p>
          <h1 className="font-display mt-1 text-2xl font-semibold tracking-tight text-white">
            {institution.name}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">{region?.name ?? "Unknown region"}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={institution.is_active ? "default" : "secondary"}>
            {institution.is_active ? "Active" : "Inactive"}
          </Badge>
          {canChangeStatus && (
            <InstitutionStatusToggle
              institutionId={institution.id}
              isActive={institution.is_active}
            />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="AICTE Permanent ID" value={institution.aicte_permanent_id ?? "—"} />
        <StatCard label="Total complaints" value={institution.total_complaint_count} />
        <StatCard
          label="Currently open"
          value={institution.open_complaint_count}
          tone={institution.open_complaint_count > 0 ? "warning" : "default"}
        />
      </div>

      {institution.address && (
        <div className="glass text-foreground/80 rounded-2xl p-4 text-sm">
          {institution.address}
        </div>
      )}

      <div>
        <h2 className="font-display mb-3 text-sm font-semibold text-white">Complaint history</h2>
        <ComplaintsTable
          complaints={complaintsPage.items}
          bureaus={bureaus}
          categories={categories}
        />
      </div>
    </div>
  );
}
