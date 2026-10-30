import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE_NAME = "casesync_session";
const PUBLIC_PATHS = new Set(["/login"]);

/**
 * Optimistic-only check (cookie presence, no API call — see
 * docs/ARCHITECTURE.md §8 and the Next.js Proxy authentication guide).
 * The real authorization decision is always made server-side against the
 * `sessions` table; this just avoids an obviously-wrong redirect flash.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSessionCookie = request.cookies.has(SESSION_COOKIE_NAME);
  const isPublicPath = PUBLIC_PATHS.has(pathname);

  if (!hasSessionCookie && !isPublicPath && pathname !== "/") {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (hasSessionCookie && isPublicPath) {
    return NextResponse.redirect(new URL("/overview", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.svg$).*)"],
};
