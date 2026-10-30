import { requireSession, hasPermission } from "@/lib/auth/session";
import { serverApiFetch } from "@/lib/api/server-client";
import { AuroraBackground } from "@/components/layout/AuroraBackground";
import { DashboardChrome } from "@/components/layout/DashboardChrome";
import type { Notification, Page } from "@/types/api";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const user = await requireSession();

  let unreadCount = 0;
  if (hasPermission(user, "notification:read")) {
    const unread = await serverApiFetch<Page<Notification>>(
      "/notifications?unread_only=true&page_size=1",
    );
    unreadCount = unread.total;
  }

  return (
    <>
      <AuroraBackground />
      <DashboardChrome user={user} unreadNotifications={unreadCount}>
        {children}
      </DashboardChrome>
    </>
  );
}
