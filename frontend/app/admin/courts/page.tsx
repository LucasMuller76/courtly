"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { courtsApi, ApiError } from "@/lib/api";
import type { Court } from "@/lib/types";
import { CourtDialog } from "./_components/court-dialog";

function formatPrice(cents: number | null): string {
  if (cents == null) return "Preço não definido";
  return (
    new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
      cents / 100,
    ) + "/h"
  );
}

export default function CourtsPage() {
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState(true);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const fetchCourts = useCallback(async () => {
    setLoading(true);
    try {
      setCourts(await courtsApi.list());
    } catch {
      toast.error("Não foi possível carregar as quadras.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    const run = async () => {
      if (!mounted) return;
      await fetchCourts();
    };
    void run();
    return () => {
      mounted = false;
    };
  }, [fetchCourts]);

  async function handleToggle(court: Court) {
    setTogglingId(court.id);
    try {
      await courtsApi.update(court.id, { is_active: !court.is_active });
      setCourts((prev) =>
        prev.map((c) =>
          c.id === court.id ? { ...c, is_active: !court.is_active } : c,
        ),
      );
      toast.success(court.is_active ? "Quadra desativada." : "Quadra ativada.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erro ao atualizar.");
    } finally {
      setTogglingId(null);
    }
  }

  async function handleDelete(court: Court) {
    try {
      await courtsApi.delete(court.id);
      setCourts((prev) => prev.filter((c) => c.id !== court.id));
      toast.success(`"${court.name}" excluída.`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erro ao excluir.");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-muted-foreground text-sm">
        Carregando quadras…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Quadras</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {courts.length === 0
              ? "Nenhuma quadra cadastrada ainda."
              : `${courts.length} quadra${courts.length > 1 ? "s" : ""} cadastrada${courts.length > 1 ? "s" : ""}`}
          </p>
        </div>
        <CourtDialog onSuccess={fetchCourts} />
      </div>

      {/* Estado vazio */}
      {courts.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-14 text-center gap-3">
            <span className="text-5xl" aria-hidden>🎾</span>
            <div>
              <p className="font-semibold">Nenhuma quadra cadastrada</p>
              <p className="text-muted-foreground text-sm mt-1">
                Adicione a primeira quadra para começar a receber reservas.
              </p>
            </div>
            <CourtDialog onSuccess={fetchCourts} />
          </CardContent>
        </Card>
      )}

      {/* Grid de quadras */}
      {courts.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {courts.map((court) => (
            <Card
              key={court.id}
              className={!court.is_active ? "opacity-60" : undefined}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {court.name}
                  </CardTitle>
                  <Badge variant={court.is_active ? "default" : "secondary"} className="shrink-0">
                    {court.is_active ? "Ativa" : "Inativa"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {formatPrice(court.price_per_hour)}
                </p>
              </CardHeader>

              <CardContent className="pt-0 flex flex-wrap gap-2">
                {/* Editar */}
                <CourtDialog court={court} onSuccess={fetchCourts} />

                {/* Ativar / Desativar */}
                <Button
                  variant="outline"
                  size="sm"
                  disabled={togglingId === court.id}
                  onClick={() => handleToggle(court)}
                >
                  {togglingId === court.id
                    ? "…"
                    : court.is_active
                      ? "Desativar"
                      : "Ativar"}
                </Button>

                {/* Excluir */}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      Excluir
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Excluir quadra?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Tem certeza que deseja excluir{" "}
                        <strong>{court.name}</strong>? Esta ação não pode ser
                        desfeita. Reservas futuras confirmadas impedem a exclusão.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        onClick={() => handleDelete(court)}
                      >
                        Excluir
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}