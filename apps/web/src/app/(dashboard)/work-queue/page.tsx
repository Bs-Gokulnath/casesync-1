import { redirect } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { serverApiFetch } from "@/lib/api/server-client";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { PageHeader } from "@/components/layout/PageHeader";
import { ComplaintsTable } from "@/features/complaints/ComplaintsTable";
import type { Bureau, Complaint, ComplaintCategory, Page } from "@/types/api";

export const metadata = { title: "Work Queue — AICTE CaseWatch" };

export default async function WorkQueuePage() {
  const user = await requireSession();
  if (!hasPermission(user, "workqueue:read")) {
    redirect("/overview");
  }

  const [mine, bureauQueue, overdue, unassigned, bureaus, categories] = await Promise.all([
    serverApiFetch<Page<Complaint>>("/work-queue/mine?page_size=50"),
    serverApiFetch<Page<Complaint>>("/work-queue/bureau?page_size=50"),
    serverApiFetch<Page<Complaint>>("/work-queue/overdue?page_size=50"),
    serverApiFetch<Page<Complaint>>("/work-queue/unassigned?page_size=50"),
    serverApiFetch<Bureau[]>("/reference/bureaus"),
    serverApiFetch<ComplaintCategory[]>("/reference/categories"),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Work Queue"
        subtitle="Cases assigned to you, your bureau's queue, overdue cases, and unassigned cases."
      />

      <Tabs defaultValue="mine">
        <TabsList>
          <TabsTrigger value="mine">Mine ({mine.total})</TabsTrigger>
          <TabsTrigger value="bureau">Bureau ({bureauQueue.total})</TabsTrigger>
          <TabsTrigger value="overdue">Overdue ({overdue.total})</TabsTrigger>
          <TabsTrigger value="unassigned">Unassigned ({unassigned.total})</TabsTrigger>
        </TabsList>
        <TabsContent value="mine" className="mt-4">
          <ComplaintsTable complaints={mine.items} bureaus={bureaus} categories={categories} />
        </TabsContent>
        <TabsContent value="bureau" className="mt-4">
          <ComplaintsTable
            complaints={bureauQueue.items}
            bureaus={bureaus}
            categories={categories}
          />
        </TabsContent>
        <TabsContent value="overdue" className="mt-4">
          <ComplaintsTable complaints={overdue.items} bureaus={bureaus} categories={categories} />
        </TabsContent>
        <TabsContent value="unassigned" className="mt-4">
          <ComplaintsTable
            complaints={unassigned.items}
            bureaus={bureaus}
            categories={categories}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
