import { redirect } from "next/navigation";
import { serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { PageHeader } from "@/components/layout/PageHeader";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { AuditEvent, Page } from "@/types/api";

export const metadata = { title: "Audit Logs — AICTE CaseWatch" };

export default async function AuditLogsPage({
  searchParams,
}: {
  searchParams: Promise<{ entity_type?: string }>;
}) {
  const user = await requireSession();
  if (!hasPermission(user, "audit:read")) {
    redirect("/overview");
  }

  const { entity_type } = await searchParams;
  const query = new URLSearchParams({ page_size: "50" });
  if (entity_type) query.set("entity_type", entity_type);

  const eventsPage = await serverApiFetch<Page<AuditEvent>>(`/audit-logs?${query.toString()}`);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs"
        subtitle={`Append-only record of every mutating action. ${eventsPage.total} event${eventsPage.total === 1 ? "" : "s"} recorded.`}
      />

      <form action="/audit-logs" method="GET" className="flex gap-2">
        <input
          type="text"
          name="entity_type"
          defaultValue={entity_type}
          placeholder="Filter by entity type (e.g. complaint)"
          className="border-input bg-input/40 placeholder:text-muted-foreground h-9 w-72 rounded-full border px-3 text-sm text-white outline-none"
        />
      </form>

      <div className="glass overflow-x-auto rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>When</TableHead>
              <TableHead>Actor</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Entity</TableHead>
              <TableHead>Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {eventsPage.items.map((event) => (
              <TableRow key={event.id}>
                <TableCell className="text-muted-foreground text-xs">
                  {new Date(event.created_at).toLocaleString("en-IN", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </TableCell>
                <TableCell className="text-sm">
                  {event.actor_id ? `User #${event.actor_id}` : "System"}
                </TableCell>
                <TableCell className="font-mono text-xs text-[#9b8dff]">{event.action}</TableCell>
                <TableCell className="text-sm">
                  {event.entity_type} #{event.entity_id}
                </TableCell>
                <TableCell className="text-muted-foreground max-w-xs truncate text-xs">
                  {event.after_json ? JSON.stringify(event.after_json) : "—"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
