"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { courtsApi, ApiError } from "@/lib/api";
import type { Court } from "@/lib/types";

const schema = z.object({
  name: z.string().min(1, "Nome é obrigatório.").max(100, "Nome muito longo."),
  price_brl: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

function parsePriceToCents(raw: string | undefined): number | null {
  if (!raw || raw.trim() === "") return null;
  const num = parseFloat(raw.replace(",", "."));
  if (isNaN(num) || num <= 0) return null;
  return Math.round(num * 100);
}

function formatCentsToInput(cents: number | null): string {
  if (cents == null) return "";
  return (cents / 100).toFixed(2);
}

interface Props {
  court?: Court;      // undefined = modo criação
  onSuccess: () => void;
}

export function CourtDialog({ court, onSuccess }: Props) {
  const [open, setOpen] = useState(false);
  const isEditing = !!court;

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  // Preenche o formulário com os dados ao abrir (modo edição)
  useEffect(() => {
    if (open) {
      reset({
        name: court?.name ?? "",
        price_brl: formatCentsToInput(court?.price_per_hour ?? null),
      });
    }
  }, [open, court, reset]);

  async function onSubmit(data: FormValues) {
    const priceCents = parsePriceToCents(data.price_brl);

    // Validação manual do preço (formato inválido)
    if (
      data.price_brl &&
      data.price_brl.trim() !== "" &&
      priceCents === null
    ) {
      setError("price_brl", { message: "Preço inválido." });
      return;
    }

    try {
      if (isEditing) {
        await courtsApi.update(court.id, {
          name: data.name,
          price_per_hour: priceCents,
        });
        toast.success("Quadra atualizada.");
      } else {
        await courtsApi.create({ name: data.name, price_per_hour: priceCents });
        toast.success("Quadra criada com sucesso.");
      }
      setOpen(false);
      onSuccess();
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Erro ao salvar quadra.",
      );
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant={isEditing ? "outline" : "default"}
          size={isEditing ? "sm" : "default"}
        >
          {isEditing ? "Editar" : "Adicionar quadra"}
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar quadra" : "Nova quadra"}</DialogTitle>
        </DialogHeader>

        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="space-y-4 mt-1"
        >
          <div className="space-y-1.5">
            <Label htmlFor="court-name">Nome</Label>
            <Input
              id="court-name"
              placeholder="Quadra 1"
              autoFocus
              {...register("name")}
            />
            {errors.name && (
              <p className="text-xs text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="court-price">
              Valor por hora{" "}
              <span className="text-muted-foreground font-normal">(opcional)</span>
            </Label>
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                R$
              </span>
              <Input
                id="court-price"
                className="pl-9"
                placeholder="80,00"
                inputMode="decimal"
                {...register("price_brl")}
              />
            </div>
            {errors.price_brl && (
              <p className="text-xs text-destructive">
                {errors.price_brl.message as string}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setOpen(false)}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Salvando…" : "Salvar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}