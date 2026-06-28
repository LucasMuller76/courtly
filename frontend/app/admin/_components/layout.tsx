import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Link from "next/link";
import type { MeResponse } from "@/lib/types";
import { AdminNav } from "./admin-nav";
import { LogoutButton } from "./logout-button";

async function getUser(): Promise<MeResponse | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("courtly_token")?.value;
  if (!token) return null;

  try {
    const res = await fetch(
      `${process.env.API_URL ?? "http://localhost:8000"}/api/v1/auth/me`,
      {
        headers: { Cookie: `courtly_token=${token}` },
        cache: "no-store",
      },
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const data = await getUser();
  if (!data) redirect("/login");

  return (
    <div className="min-h-screen bg-background">
      {/* Topbar */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="flex h-13 items-center justify-between px-4 max-w-screen-xl mx-auto">
          <Link
            href="/admin/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <span className="text-lg" aria-hidden>🎾</span>
            <span className="font-bold text-sm tracking-tight">Courtly</span>
            {data.club && (
              <>
                <span className="text-muted-foreground/40 mx-0.5">/</span>
                <span className="text-sm text-muted-foreground font-medium">
                  {data.club.name}
                </span>
              </>
            )}
          </Link>

          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:block">
              {data.user.name}
            </span>
            <LogoutButton />
          </div>
        </div>
      </header>

      {/* Nav secundária */}
      <AdminNav />

      {/* Conteúdo */}
      <main className="max-w-screen-xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}