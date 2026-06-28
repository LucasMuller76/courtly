"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/admin/dashboard", label: "Início" },
  { href: "/admin/courts",    label: "Quadras" },
  // próximas etapas:
  // { href: "/admin/reservations", label: "Reservas" },
  // { href: "/admin/settings",     label: "Configurações" },
];

export function AdminNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Menu do painel"
      className="flex items-center gap-1 border-b border-border"
    >
      <div className="flex items-center gap-1 max-w-screen-xl mx-auto w-full px-4">
        {NAV_ITEMS.map(({ href, label }) => {
          const active =
            pathname === href ||
            (href !== "/admin/dashboard" && pathname.startsWith(href));

          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "relative px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "text-foreground after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:rounded-full after:bg-primary"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}