import { serverApiFetch } from "@/lib/api/server-client";
import { PageHeader } from "@/components/layout/PageHeader";
import { NotificationsList } from "@/features/notifications/NotificationsList";
import type { Notification, Page } from "@/types/api";

export const metadata = { title: "Notifications — AICTE CaseWatch" };

export default async function NotificationsPage() {
  const notificationsPage = await serverApiFetch<Page<Notification>>("/notifications?page_size=50");

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        subtitle="Assignments, transfers, escalations and overlap alerts relevant to you or your bureau."
      />
      <NotificationsList notifications={notificationsPage.items} />
    </div>
  );
}
