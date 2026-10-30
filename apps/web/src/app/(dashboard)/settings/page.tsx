import { redirect } from "next/navigation";
import { requireSession, hasPermission } from "@/lib/auth/session";
import { serverApiFetch } from "@/lib/api/server-client";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/layout/PageHeader";
import { ReferenceEntityManager } from "@/features/admin/ReferenceEntityManager";
import { UsersManager } from "@/features/admin/UsersManager";
import type { AdminBureau, AdminCategory, AdminRegion, AdminUser } from "@/types/api";

export const metadata = { title: "Settings — AICTE CaseWatch" };

export default async function SettingsPage() {
  const user = await requireSession();
  if (!hasPermission(user, "admin:manage")) {
    redirect("/overview");
  }

  const [bureaus, regions, categories, users] = await Promise.all([
    serverApiFetch<AdminBureau[]>("/admin/bureaus"),
    serverApiFetch<AdminRegion[]>("/admin/regions"),
    serverApiFetch<AdminCategory[]>("/admin/categories"),
    serverApiFetch<AdminUser[]>("/admin/users"),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Administration"
        subtitle="Manage bureaus, regions, complaint categories and user accounts."
      />

      <Tabs defaultValue="bureaus">
        <TabsList>
          <TabsTrigger value="bureaus">Bureaus</TabsTrigger>
          <TabsTrigger value="regions">Regions</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
        </TabsList>
        <TabsContent value="bureaus" className="mt-4">
          <ReferenceEntityManager
            title="Bureaus"
            basePath="/admin/bureaus"
            items={bureaus}
            hasDescription
          />
        </TabsContent>
        <TabsContent value="regions" className="mt-4">
          <ReferenceEntityManager title="Regions" basePath="/admin/regions" items={regions} />
        </TabsContent>
        <TabsContent value="categories" className="mt-4">
          <ReferenceEntityManager
            title="Categories"
            basePath="/admin/categories"
            items={categories}
            hasDescription
          />
        </TabsContent>
        <TabsContent value="users" className="mt-4">
          <UsersManager users={users} bureaus={bureaus} regions={regions} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
