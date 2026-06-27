"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { authApi } from "@/lib/api";

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await authApi.logout();
    } finally {
      // Garante o redirect mesmo se a chamada falhar
      router.push("/login");
      router.refresh();
    }
  }

  return (
    <Button variant="ghost" size="sm" onClick={handleLogout}>
      Sair
    </Button>
  );
}