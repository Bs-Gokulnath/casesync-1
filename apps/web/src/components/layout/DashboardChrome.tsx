"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Menu } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { UserMenu } from "@/components/layout/UserMenu";
import { GlobalSearch } from "@/components/layout/GlobalSearch";
import { PageTransition } from "@/components/layout/PageTransition";
import type { UserProfile } from "@/types/api";

export function DashboardChrome({
  user,
  unreadNotifications,
  children,
}: {
  user: UserProfile;
  unreadNotifications: number;
  children: React.ReactNode;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile drawer backdrop */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setMobileOpen(false)}
            className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
            aria-hidden
          />
        )}
      </AnimatePresence>

      <div
        className={`fixed inset-y-0 left-0 z-40 transition-transform duration-300 ease-out lg:static lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <Sidebar
          user={user}
          unreadNotifications={unreadNotifications}
          onNavigate={() => setMobileOpen(false)}
        />
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-border/60 glass sticky top-0 z-20 flex h-16 shrink-0 items-center justify-between gap-3 border-b px-4 sm:px-6">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="text-muted-foreground hover:text-foreground shrink-0 rounded-lg p-2 hover:bg-white/5 lg:hidden"
            aria-label="Open navigation"
          >
            <Menu className="size-5" />
          </button>
          <GlobalSearch />
          <UserMenu user={user} />
        </header>
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <PageTransition>{children}</PageTransition>
          </div>
        </main>
      </div>
    </div>
  );
}
