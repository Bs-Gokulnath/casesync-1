"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { LogOut, User as UserIcon } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api/browser-client";
import type { UserProfile } from "@/types/api";

const ROLE_LABELS: Record<string, string> = {
  system_admin: "System Administrator",
  senior_management: "Senior Management",
  bureau_officer: "Bureau Officer",
  regional_officer: "Regional Officer",
  auditor: "Auditor",
};

export function UserMenu({ user }: { user: UserProfile }) {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } finally {
      router.push("/login");
      router.refresh();
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="gap-2.5 rounded-full px-2 hover:bg-white/5">
          <span className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-[#7c6cff] to-[#22d3ee] p-[1.5px]">
            <span className="bg-card flex size-full items-center justify-center rounded-full text-xs font-semibold text-white">
              {user.full_name.slice(0, 1).toUpperCase()}
            </span>
          </span>
          <span className="hidden text-left sm:block">
            <span className="block text-sm font-medium text-white">{user.full_name}</span>
            <span className="text-muted-foreground block text-xs">
              {ROLE_LABELS[user.role] ?? user.role}
            </span>
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="glass w-56 border-white/10">
        <DropdownMenuLabel className="text-muted-foreground flex items-center gap-2">
          <UserIcon className="size-4" />
          {user.email}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={handleLogout} disabled={loggingOut} variant="destructive">
          <LogOut className="size-4" />
          {loggingOut ? "Signing out..." : "Sign out"}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
