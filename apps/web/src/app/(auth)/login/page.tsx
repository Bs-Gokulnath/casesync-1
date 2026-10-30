import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth/session";
import { AuroraBackground } from "@/components/layout/AuroraBackground";
import { LoginCard } from "@/features/auth/LoginCard";

export const metadata = { title: "Sign in — AICTE CaseWatch" };

export default async function LoginPage() {
  const session = await getSession();
  if (session) {
    redirect("/overview");
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <AuroraBackground intensity="bold" />
      <LoginCard />
    </div>
  );
}
