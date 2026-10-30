import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const COMPLAINT_STATUS_STYLES: Record<string, string> = {
  received: "bg-slate-500/10 text-slate-300 border-slate-500/30",
  under_review: "bg-sky-500/10 text-sky-300 border-sky-500/30",
  under_process: "bg-[#7c6cff]/10 text-[#b3a8ff] border-[#7c6cff]/30",
  pending_information: "bg-amber-500/10 text-amber-300 border-amber-500/30",
  transferred: "bg-fuchsia-500/10 text-fuchsia-300 border-fuchsia-500/30",
  escalated: "bg-orange-500/10 text-orange-300 border-orange-500/30",
  disposed: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
};

const OVERLAP_STATUS_STYLES: Record<string, string> = {
  open: "bg-amber-500/10 text-amber-300 border-amber-500/30",
  confirmed: "bg-rose-500/10 text-rose-300 border-rose-500/30",
  dismissed: "bg-slate-500/10 text-slate-400 border-slate-500/30",
  resolved: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
};

const PRIORITY_STYLES: Record<string, string> = {
  low: "bg-slate-500/10 text-slate-400 border-slate-500/30",
  medium: "bg-sky-500/10 text-sky-300 border-sky-500/30",
  high: "bg-orange-500/10 text-orange-300 border-orange-500/30",
  critical: "bg-rose-500/10 text-rose-300 border-rose-500/30",
};

function labelize(value: string): string {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge variant="outline" className={cn("border", COMPLAINT_STATUS_STYLES[status])}>
      {labelize(status)}
    </Badge>
  );
}

export function OverlapStatusBadge({ status }: { status: string }) {
  return (
    <Badge variant="outline" className={cn("border", OVERLAP_STATUS_STYLES[status])}>
      {labelize(status)}
    </Badge>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  return (
    <Badge variant="outline" className={cn("border", PRIORITY_STYLES[priority])}>
      {labelize(priority)}
    </Badge>
  );
}
