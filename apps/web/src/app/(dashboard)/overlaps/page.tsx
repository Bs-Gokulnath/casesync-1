import Link from "next/link";
import { requireSession } from "@/lib/auth/session";
import { serverApiFetch } from "@/lib/api/server-client";
import { PageHeader } from "@/components/layout/PageHeader";
import { OverlapStatusBadge } from "@/components/data-display/StatusBadge";
import { OverlapDecisionDialog } from "@/features/overlaps/OverlapDecisionDialog";
import type { Institution, OverlapAlert, Page } from "@/types/api";

export const metadata = { title: "Overlaps — AICTE CaseWatch" };

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "All" },
  { value: "open", label: "Open" },
  { value: "confirmed", label: "Confirmed" },
  { value: "dismissed", label: "Dismissed" },
  { value: "resolved", label: "Resolved" },
];

export default async function OverlapsPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const { status } = await searchParams;
  const user = await requireSession();

  const query = new URLSearchParams({ page_size: "50" });
  if (status) query.set("status", status);

  const [alertsPage, institutionsPage] = await Promise.all([
    serverApiFetch<Page<OverlapAlert>>(`/overlaps?${query.toString()}`),
    serverApiFetch<Page<Institution>>("/institutions?page_size=100"),
  ]);

  const institutionNameById = new Map(institutionsPage.items.map((i) => [i.id, i.name]));
  const canDecide = user.permissions.includes("overlap:decide");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cross-Bureau Overlaps"
        subtitle="Institutions with complaints open across more than one bureau, or flagged as possible duplicates. Reviewing an alert never changes the underlying cases automatically."
      />

      <form action="/overlaps" method="GET" className="flex gap-2">
        <select
          name="status"
          defaultValue={status ?? ""}
          className="border-input bg-input/40 h-9 rounded-full border px-3 text-sm text-white outline-none [&>option]:bg-[#0c0e19]"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </form>

      {alertsPage.items.length === 0 ? (
        <div className="text-muted-foreground rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm">
          No overlap alerts match this filter.
        </div>
      ) : (
        <div className="space-y-3">
          {alertsPage.items.map((alert) => (
            <div key={alert.id} className="glass overlap-alert-card rounded-2xl p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <OverlapStatusBadge status={alert.status} />
                    <span className="text-sm font-medium text-white">
                      {institutionNameById.get(alert.institution_id) ??
                        `Institution #${alert.institution_id}`}
                    </span>
                  </div>
                  <p className="text-foreground/80 mt-2 text-sm">{alert.rationale}</p>
                  <p className="text-muted-foreground mt-2 text-xs">
                    Confidence {(alert.confidence_score * 100).toFixed(0)}% &middot; Cases:{" "}
                    {alert.case_ids.map((id, i) => (
                      <span key={id}>
                        {i > 0 && ", "}
                        <Link href={`/complaints/${id}`} className="text-[#9b8dff] underline">
                          #{id}
                        </Link>
                      </span>
                    ))}
                  </p>
                  {alert.decision_reason && (
                    <p className="text-muted-foreground mt-2 text-xs">
                      Decision: {alert.decision_reason}
                    </p>
                  )}
                </div>
                {canDecide && alert.status === "open" && <OverlapDecisionDialog alert={alert} />}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
