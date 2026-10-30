"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { motion } from "motion/react";
import {
  LayoutDashboard,
  Building2,
  FileText,
  GitMerge,
  ListChecks,
  BarChart3,
  Bell,
  History,
  Settings,
  ChevronsLeft,
  ChevronsRight,
  Radar,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { UserProfile } from "@/types/api";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  permission?: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/institutions", label: "Institutions", icon: Building2, permission: "institution:read" },
  { href: "/complaints", label: "Complaints", icon: FileText, permission: "complaint:read" },
  { href: "/overlaps", label: "Overlaps", icon: GitMerge, permission: "overlap:read" },
  { href: "/work-queue", label: "Work Queue", icon: ListChecks, permission: "workqueue:read" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, permission: "analytics:read" },
  { href: "/notifications", label: "Notifications", icon: Bell, permission: "notification:read" },
  { href: "/audit-logs", label: "Audit Logs", icon: History, permission: "audit:read" },
  { href: "/settings", label: "Settings", icon: Settings, permission: "admin:manage" },
];

export function Sidebar({
  user,
  unreadNotifications = 0,
  onNavigate,
}: {
  user: UserProfile;
  unreadNotifications?: number;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const items = NAV_ITEMS.filter(
    (item) => !item.permission || user.permissions.includes(item.permission),
  );

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 248 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="glass relative z-10 flex h-full shrink-0 flex-col border-r"
    >
      <div className="border-sidebar-border flex h-16 items-center gap-2.5 border-b px-4">
        <div className="relative flex size-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#7c6cff] to-[#22d3ee] shadow-[0_0_20px_-4px_#7c6cff]">
          <Radar className="size-4 text-white" strokeWidth={2.5} />
        </div>
        {!collapsed && (
          <span className="font-display truncate text-sm font-semibold tracking-tight text-white">
            AICTE CaseWatch
          </span>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3" aria-label="Primary">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                active ? "text-white" : "text-muted-foreground hover:text-foreground",
              )}
              aria-current={active ? "page" : undefined}
            >
              {active && (
                <motion.span
                  layoutId="sidebar-active-pill"
                  className="glow-primary absolute inset-0 rounded-xl bg-gradient-to-r from-[#7c6cff] to-[#9b6cff]"
                  transition={{ type: "spring", stiffness: 350, damping: 32 }}
                />
              )}
              <Icon className="relative z-10 size-4 shrink-0" />
              {!collapsed && <span className="relative z-10 truncate">{item.label}</span>}
              {item.href === "/notifications" && unreadNotifications > 0 && (
                <span
                  className={cn(
                    "relative z-10 ml-auto flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-xs font-semibold",
                    active ? "bg-white/20 text-white" : "bg-[#fb4570] text-white",
                  )}
                >
                  {unreadNotifications > 99 ? "99+" : unreadNotifications}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      <button
        type="button"
        onClick={() => setCollapsed((v) => !v)}
        className="border-sidebar-border text-muted-foreground hover:text-foreground hidden items-center gap-2 border-t px-4 py-3.5 text-xs transition-colors hover:bg-white/5 lg:flex"
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <ChevronsRight className="size-4" /> : <ChevronsLeft className="size-4" />}
        {!collapsed && "Collapse"}
      </button>
    </motion.aside>
  );
}
