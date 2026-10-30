import Link from "next/link";
import { notFound } from "next/navigation";
import { AlertTriangle } from "lucide-react";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { ApiError, serverApiFetch } from "@/lib/api/server-client";
import { StatusBadge, PriorityBadge } from "@/components/data-display/StatusBadge";
import { CaseTimeline } from "@/features/complaints/CaseTimeline";
import { DocumentsSection } from "@/features/complaints/DocumentsSection";
import { WorkflowActions } from "@/features/workflow/WorkflowActions";
import type {
  Bureau,
  Complaint,
  ComplaintCategory,
  Document,
  Institution,
  OverlapAlert,
  Page,
  TimelineEntry,
} from "@/types/api";

export const metadata = { title: "Complaint — AICTE CaseWatch" };

export default async function ComplaintDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await requireSession();

  let complaint: Complaint;
  try {
    complaint = await serverApiFetch<Complaint>(`/complaints/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const [institution, categories, bureaus, timeline, relatedOverlaps, documents] =
    await Promise.all([
      serverApiFetch<Institution>(`/institutions/${complaint.institution_id}`),
      serverApiFetch<ComplaintCategory[]>("/reference/categories"),
      serverApiFetch<Bureau[]>("/reference/bureaus"),
      serverApiFetch<TimelineEntry[]>(`/complaints/${id}/history`),
      user.permissions.includes("overlap:read")
        ? serverApiFetch<Page<OverlapAlert>>(
            `/overlaps?institution_id=${complaint.institution_id}&page_size=50`,
          )
        : Promise.resolve<Page<OverlapAlert>>({ items: [], total: 0, page: 1, page_size: 50 }),
      hasPermission(user, "document:read")
        ? serverApiFetch<Document[]>(`/complaints/${id}/documents`)
        : Promise.resolve<Document[]>([]),
    ]);

  const category = categories.find((c) => c.id === complaint.category_id);
  const bureau = bureaus.find((b) => b.id === complaint.bureau_id);
  const alertsForThisCase = relatedOverlaps.items.filter(
    (a) => a.case_ids.includes(complaint.id) && a.status === "open",
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-[#9b8dff]">{complaint.case_reference}</p>
          <h1 className="font-display mt-1 text-2xl font-semibold tracking-tight text-white">
            {complaint.subject}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={complaint.status} />
            <PriorityBadge priority={complaint.priority} />
          </div>
        </div>
        {user.permissions.some((p) => p.startsWith("complaint:")) && (
          <WorkflowActions complaint={complaint} bureaus={bureaus} permissions={user.permissions} />
        )}
      </div>

      {alertsForThisCase.length > 0 && (
        <div className="glass glow-accent rounded-2xl border-amber-500/20 bg-amber-500/5 p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-400" />
            <div>
              <p className="text-sm font-semibold text-amber-200">
                Potential Overlapping Cases — Coordination Required
              </p>
              {alertsForThisCase.map((alert) => (
                <div key={alert.id} className="mt-2 text-sm text-amber-100/80">
                  <p>{alert.rationale}</p>
                  <p className="mt-1 text-xs text-amber-300/80">
                    Confidence {(alert.confidence_score * 100).toFixed(0)}% &middot;{" "}
                    <Link href="/overlaps" className="underline">
                      Review in Overlaps
                    </Link>
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section className="glass rounded-2xl p-5">
            <h2 className="font-display text-sm font-semibold text-white">Description</h2>
            <p className="text-foreground/80 mt-2 text-sm whitespace-pre-wrap">
              {complaint.description}
            </p>
            {complaint.disposal_note && (
              <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3">
                <p className="text-xs font-medium text-emerald-300">Disposal note</p>
                <p className="mt-1 text-sm text-emerald-100/90">{complaint.disposal_note}</p>
              </div>
            )}
          </section>

          <section className="glass rounded-2xl p-5">
            <h2 className="font-display text-sm font-semibold text-white">Activity timeline</h2>
            <div className="mt-4">
              <CaseTimeline entries={timeline} bureaus={bureaus} />
            </div>
          </section>

          {hasPermission(user, "document:read") && (
            <DocumentsSection
              complaintId={complaint.id}
              documents={documents}
              canUpload={hasPermission(user, "document:upload")}
            />
          )}
        </div>

        <aside className="space-y-4">
          <section className="glass rounded-2xl p-5 text-sm">
            <h2 className="font-display text-sm font-semibold text-white">Case details</h2>
            <dl className="mt-3 space-y-2.5">
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Institution</dt>
                <dd>
                  <Link
                    href={`/institutions/${institution.id}`}
                    className="font-medium text-white hover:text-[#9b8dff] hover:underline"
                  >
                    {institution.name}
                  </Link>
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Category</dt>
                <dd className="font-medium text-white">{category?.name ?? "—"}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Bureau</dt>
                <dd className="font-medium text-white">{bureau?.name ?? "—"}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Received</dt>
                <dd className="font-medium text-white">
                  {new Date(complaint.received_date).toLocaleDateString("en-IN")}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Expected disposal</dt>
                <dd className="font-medium text-white">
                  {complaint.expected_disposal_date
                    ? new Date(complaint.expected_disposal_date).toLocaleDateString("en-IN")
                    : "—"}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Assigned officer</dt>
                <dd className="font-medium text-white">
                  {complaint.assigned_officer_id
                    ? `Officer #${complaint.assigned_officer_id}`
                    : "Unassigned"}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Source</dt>
                <dd className="font-medium text-white capitalize">
                  {complaint.source.replace("_", " ")}
                </dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}
