import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatCard } from "@/components/data-display/StatCard";
import { OverlapStatusBadge } from "@/components/data-display/StatusBadge";
import { CountBarChart } from "@/features/analytics/CountBarChart";
import { serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import type { AnalyticsSummary } from "@/types/api";

export const metadata = { title: "Analytics — AICTE CaseWatch" };

export default async function AnalyticsPage({
  searchParams,
}: {
  searchParams: Promise<{ date_from?: string; date_to?: string }>;
}) {
  const user = await requireSession();
  const { date_from, date_to } = await searchParams;

  const query = new URLSearchParams();
  if (date_from) query.set("date_from", date_from);
  if (date_to) query.set("date_to", date_to);

  const summary = await serverApiFetch<AnalyticsSummary>(`/analytics/summary?${query.toString()}`);
  const canExport = hasPermission(user, "analytics:export");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        subtitle="Derived from persisted complaint records; updates as cases move."
        action={
          canExport && (
            <Button variant="outline" asChild>
              <a href={`/api/v1/analytics/export.csv?${query.toString()}`}>
                <Download className="size-4" />
                Export CSV
              </a>
            </Button>
          )
        }
      />

      <form action="/analytics" method="GET" className="flex flex-wrap items-end gap-3">
        <div>
          <label htmlFor="date_from" className="text-muted-foreground block text-xs font-medium">
            From
          </label>
          <input
            id="date_from"
            type="date"
            name="date_from"
            defaultValue={date_from}
            className="border-input bg-input/40 mt-1 h-9 rounded-lg border px-2 text-sm text-white outline-none"
          />
        </div>
        <div>
          <label htmlFor="date_to" className="text-muted-foreground block text-xs font-medium">
            To
          </label>
          <input
            id="date_to"
            type="date"
            name="date_to"
            defaultValue={date_to}
            className="border-input bg-input/40 mt-1 h-9 rounded-lg border px-2 text-sm text-white outline-none"
          />
        </div>
        <Button type="submit" variant="secondary">
          Apply
        </Button>
      </form>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total complaints" value={summary.total} />
        <StatCard label="Overdue" value={summary.overdue_count} tone="danger" />
        <StatCard label="Disposal rate" value={`${(summary.disposal_rate * 100).toFixed(0)}%`} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CountBarChart title="By status" data={summary.by_status} />
        <CountBarChart title="By bureau" data={summary.by_bureau} />
        <CountBarChart title="By category" data={summary.by_category} />
        <CountBarChart title="By region" data={summary.by_region} />
      </div>

      <div className="glass rounded-2xl p-5">
        <h3 className="font-display text-sm font-semibold text-white">Overlap outcomes</h3>
        <div className="mt-3 flex flex-wrap gap-4">
          {summary.overlap_by_status.map((row) => (
            <div key={row.key} className="flex items-center gap-2">
              <OverlapStatusBadge status={row.key} />
              <span className="text-foreground/80 text-sm font-medium">{row.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
