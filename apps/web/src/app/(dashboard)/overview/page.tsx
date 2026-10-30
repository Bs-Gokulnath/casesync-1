import Link from "next/link";
import { AlertTriangle, ArrowRight, Sparkles } from "lucide-react";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { serverApiFetch } from "@/lib/api/server-client";
import { StatCard } from "@/components/data-display/StatCard";
import type { Page, Institution, Complaint, OverlapAlert } from "@/types/api";

export const metadata = { title: "Overview — AICTE CaseWatch" };

async function safeTotal<T>(path: string): Promise<number | null> {
  try {
    const page = await serverApiFetch<Page<T>>(path);
    return page.total;
  } catch {
    return null;
  }
}

export default async function OverviewPage() {
  const user = await requireSession();

  const [institutionTotal, complaintTotal, openComplaintTotal, openOverlapTotal] =
    await Promise.all([
      hasPermission(user, "institution:read")
        ? safeTotal<Institution>("/institutions?page_size=1")
        : null,
      hasPermission(user, "complaint:read")
        ? safeTotal<Complaint>("/complaints?page_size=1")
        : null,
      hasPermission(user, "complaint:read")
        ? safeTotal<Complaint>("/complaints?page_size=1&status=under_review")
        : null,
      hasPermission(user, "overlap:read")
        ? safeTotal<OverlapAlert>("/overlaps?page_size=1&status=open")
        : null,
    ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Sparkles className="size-5 text-[#22d3ee]" />
        <div>
          <h1 className="font-display text-2xl font-semibold tracking-tight text-white">
            Welcome, {user.full_name}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            A unified view of institution complaints across AICTE bureaus and cells.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {institutionTotal !== null && <StatCard label="Institutions" value={institutionTotal} />}
        {complaintTotal !== null && <StatCard label="Total complaints" value={complaintTotal} />}
        {openComplaintTotal !== null && (
          <StatCard label="Under review" value={openComplaintTotal} tone="warning" />
        )}
        {openOverlapTotal !== null && (
          <StatCard
            label="Open overlap alerts"
            value={openOverlapTotal}
            tone={openOverlapTotal > 0 ? "danger" : "default"}
          />
        )}
      </div>

      {openOverlapTotal !== null && openOverlapTotal > 0 && (
        <Link
          href="/overlaps"
          className="group glass glow-accent flex items-center gap-3 rounded-2xl border-amber-500/20 bg-amber-500/5 p-4 text-sm font-medium text-amber-200 transition-colors hover:bg-amber-500/10"
        >
          <AlertTriangle className="size-5 shrink-0 text-amber-400" />
          <span>
            Potential Overlapping Cases — Coordination Required: {openOverlapTotal} alert
            {openOverlapTotal === 1 ? "" : "s"} awaiting review.
          </span>
          <ArrowRight className="ml-auto size-4 shrink-0 transition-transform group-hover:translate-x-1" />
        </Link>
      )}

      {hasPermission(user, "analytics:read") && (
        <Link
          href="/analytics"
          className="group glass flex items-center gap-3 rounded-2xl p-4 text-sm text-slate-300 transition-colors hover:bg-white/5"
        >
          <span>
            See trends by status, bureau, region and category, overdue counts, and the disposal rate
            in <span className="font-medium text-white">Analytics</span>
          </span>
          <ArrowRight className="ml-auto size-4 shrink-0 transition-transform group-hover:translate-x-1" />
        </Link>
      )}
    </div>
  );
}
