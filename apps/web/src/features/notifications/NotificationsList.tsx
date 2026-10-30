"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { BellOff, CheckCheck } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api/browser-client";
import type { Notification } from "@/types/api";

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

function linkFor(notification: Notification): string | null {
  if (notification.related_complaint_id) return `/complaints/${notification.related_complaint_id}`;
  if (notification.related_overlap_alert_id) return "/overlaps";
  return null;
}

export function NotificationsList({ notifications }: { notifications: Notification[] }) {
  const router = useRouter();

  async function markRead(id: number) {
    try {
      await apiFetch(`/notifications/${id}/read`, { method: "POST" });
      router.refresh();
    } catch {
      toast.error("Could not update notification");
    }
  }

  async function markAllRead() {
    try {
      await apiFetch("/notifications/read-all", { method: "POST" });
      router.refresh();
    } catch {
      toast.error("Could not update notifications");
    }
  }

  const hasUnread = notifications.some((n) => !n.is_read);

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button variant="outline" size="sm" onClick={markAllRead} disabled={!hasUnread}>
          <CheckCheck className="size-4" />
          Mark all read
        </Button>
      </div>

      {notifications.length === 0 ? (
        <div className="text-muted-foreground rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm">
          <BellOff className="mx-auto mb-2 size-5 text-white/30" />
          No notifications yet.
        </div>
      ) : (
        <ul className="glass divide-border/60 divide-y rounded-2xl">
          {notifications.map((n) => {
            const href = linkFor(n);
            const content = (
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{n.title}</p>
                <p className="text-foreground/70 mt-0.5 text-sm">{n.message}</p>
                <p className="text-muted-foreground mt-1 text-xs">{formatDateTime(n.created_at)}</p>
              </div>
            );
            return (
              <li
                key={n.id}
                className={`flex items-start gap-3 p-4 ${n.is_read ? "" : "bg-[#7c6cff]/5"}`}
              >
                {!n.is_read && (
                  <span
                    className="mt-1.5 size-2 shrink-0 rounded-full bg-[#22d3ee] shadow-[0_0_8px_1px_#22d3ee]"
                    aria-hidden
                  />
                )}
                {href ? (
                  <Link href={href} className="flex-1 hover:underline">
                    {content}
                  </Link>
                ) : (
                  content
                )}
                {!n.is_read && (
                  <Button variant="ghost" size="sm" onClick={() => markRead(n.id)}>
                    Mark read
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
