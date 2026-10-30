import "server-only";
import { cache } from "react";
import { redirect } from "next/navigation";
import { ApiError, serverApiFetch } from "@/lib/api/server-client";
import type { UserProfile } from "@/types/api";

/**
 * The current user's profile, or null if not authenticated. Memoized per
 * request with React's cache() so multiple Server Components calling this
 * in the same render only hit the API once.
 */
export const getSession = cache(async (): Promise<UserProfile | null> => {
  try {
    return await serverApiFetch<UserProfile>("/auth/me");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
});

/** For Server Components that must be authenticated — redirects to /login otherwise. */
export async function requireSession(): Promise<UserProfile> {
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }
  return session;
}

export function hasPermission(user: UserProfile, permission: string): boolean {
  return user.permissions.includes(permission);
}
