"use client";

import { motion } from "motion/react";
import { Clock } from "lucide-react";
import type { Bureau, TimelineEntry } from "@/types/api";

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function describe(entry: TimelineEntry, bureauNameById: Map<number, string>): string {
  if (entry.kind === "status_change") {
    const from = entry.from_status ? entry.from_status.replace("_", " ") : "new case";
    return `Status changed from "${from}" to "${entry.to_status.replace("_", " ")}"`;
  }
  switch (entry.action_type) {
    case "transfer": {
      const from = entry.from_bureau_id ? bureauNameById.get(entry.from_bureau_id) : null;
      const to = entry.to_bureau_id ? bureauNameById.get(entry.to_bureau_id) : null;
      return `Transferred${from ? ` from ${from}` : ""}${to ? ` to ${to}` : ""}`;
    }
    case "escalate":
      return "Case escalated";
    case "dispose":
      return "Case disposed";
    case "reopen":
      return "Case reopened";
    case "assign":
      return entry.note ?? "Officer assigned";
    default:
      return "Note added";
  }
}

export function CaseTimeline({
  entries,
  bureaus,
}: {
  entries: TimelineEntry[];
  bureaus: Bureau[];
}) {
  const bureauNameById = new Map(bureaus.map((b) => [b.id, b.name]));

  if (entries.length === 0) {
    return <p className="text-muted-foreground text-sm">No activity recorded yet.</p>;
  }

  const ordered = [...entries].reverse();

  return (
    <ol className="relative space-y-5">
      {ordered.map((entry, index) => (
        <motion.li
          key={index}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05, duration: 0.3 }}
          className="relative flex gap-3"
        >
          {index !== ordered.length - 1 && (
            <span className="absolute top-6 left-3 h-full w-px bg-gradient-to-b from-[#7c6cff]/40 to-transparent" />
          )}
          <div className="relative z-10 mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#7c6cff] to-[#22d3ee] shadow-[0_0_10px_-2px_#7c6cff]">
            <Clock className="size-3.5 text-white" />
          </div>
          <div className="border-border/60 min-w-0 flex-1 border-b pb-4 last:border-0 last:pb-0">
            <p className="text-sm font-medium text-white">{describe(entry, bureauNameById)}</p>
            {entry.reason && <p className="text-foreground/70 mt-0.5 text-sm">{entry.reason}</p>}
            <p className="text-muted-foreground mt-1 text-xs">
              {entry.actor_name} &middot; {formatDateTime(entry.created_at)}
            </p>
          </div>
        </motion.li>
      ))}
    </ol>
  );
}
