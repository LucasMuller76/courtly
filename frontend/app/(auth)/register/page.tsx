"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { authApi, ApiError } from "@/lib/api";

// Converte texto para slug URL-safe (roda no browser, sem lib extra)
function toSlug(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove acentos
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

const schema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres."),
  email: z.string().email("E-mail inválido."),
  password: z.string().min(8, "Senha deve ter pelo menos 8 caracteres."),
  club_name: z.string().min(2, "Nome do clube deve ter pelo menos 2 caracteres."),
  club_slug: z
    .string()
    .min(3, "Endereço deve ter pelo menos 3 caracteres.")
    .regex(/^[a-z0-9-]+$/, "Use apenas letras minúsculas, números e hífens."),
});

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const [slugEdited, setSlugEdited] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const clubSlug = watch("club_slug") ?? "";

  async function onSubmit(data: FormValues) {
    setServerError(null);
    try {
      await authApi.register(data);
      router.push("/admin/dashboard");
      router.refresh();
    } catch (err) {
      setServerError(
        err instanceof ApiError ? err.message : "Erro inesperado. Tente novamente.",
      );
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl" aria-hidden>🎾</span>
          <span className="text-xl font-bold tracking-tight">Courtly</span>
        </div>
        <CardTitle className="text-lg">Criar sua conta</CardTitle>
        <CardDescription>
          Configure seu clube e comece a automatizar reservas
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
          {serverError && (
            <div
              role="alert"
              className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md px-3 py-2"
            >
              {serverError}
            </div>
          )}

          {/* Seção: dados pessoais */}
          <div className="space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Sua conta
            </p>

            <div className="space-y-1.5">
              <Label htmlFor="name">Seu nome</Label>
              <Input
                id="name"
                placeholder="João Silva"
                autoComplete="name"
                {...register("name")}
              />
              {errors.name && (
                <p className="text-xs text-destructive">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="joao@meuclube.com"
                autoComplete="email"
                {...register("email")}
              />
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                autoComplete="new-password"
                {...register("password")}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>
          </div>

          {/* Divisor */}
          <div className="border-t border-border" />

          {/* Seção: dados do clube */}
          <div className="space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Seu clube
            </p>

            <div className="space-y-1.5">
              <Label htmlFor="club_name">Nome do clube</Label>
              <Input
                id="club_name"
                placeholder="Arena 360 Padel"
                {...register("club_name", {
                  onChange: (e) => {
                    // Auto-preenche o slug enquanto o usuário não tiver editado manualmente
                    if (!slugEdited) {
                      setValue("club_slug", toSlug(e.target.value), {
                        shouldValidate: true,
                      });
                    }
                  },
                })}
              />
              {errors.club_name && (
                <p className="text-xs text-destructive">{errors.club_name.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="club_slug">Endereço de reservas</Label>
              {/* Input com prefixo — estilizado para combinar com shadcn Input */}
              <div className="flex items-center rounded-md border border-input bg-input overflow-hidden focus-within:outline-none focus-within:ring-2 focus-within:ring-ring">
                <span className="px-3 py-2 text-sm text-muted-foreground bg-muted border-r border-border select-none whitespace-nowrap">
                  /book/
                </span>
                <input
                  id="club_slug"
                  className="flex-1 px-3 py-2 text-sm bg-transparent outline-none placeholder:text-muted-foreground"
                  placeholder="arena-360"
                  {...register("club_slug", {
                    onChange: () => setSlugEdited(true),
                  })}
                />
              </div>
              {errors.club_slug ? (
                <p className="text-xs text-destructive">{errors.club_slug.message}</p>
              ) : clubSlug ? (
                <p className="text-xs text-muted-foreground">
                  Jogadores vão acessar em:{" "}
                  <span className="text-foreground font-medium">
                    courtly.app/book/{clubSlug}
                  </span>
                </p>
              ) : null}
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Criando conta…" : "Criar conta e começar"}
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground mt-5">
          Já tem conta?{" "}
          <Link href="/login" className="text-primary hover:underline font-medium">
            Entrar
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}