import "server-only";
import { cookies } from "next/headers";

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API request failed with status ${status}`);
  }
}

const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

/**
 * Server-side fetch to the FastAPI service, used by Server Components for
 * reads. Forwards the browser's incoming cookies so the backend can resolve
 * the session. Never used for mutations — those go through the browser's
 * own fetch to the same-origin `/api/*` proxy so Set-Cookie responses land
 * in the real browser (see docs/ARCHITECTURE.md).
 */
export async function serverApiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");

  const response = await fetch(`${API_INTERNAL_URL}/api/v1${path}`, {
    ...init,
    headers: {
      ...init?.headers,
      Cookie: cookieHeader,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      // response had no JSON body
    }
    throw new ApiError(response.status, body);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
