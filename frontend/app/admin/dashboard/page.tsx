import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { MeResponse } from "@/lib/types";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

async function getDashboardData(): Promise<MeResponse> {
  const cookieStore = await cookies();
  const token = cookieStore.get("courtly_token")?.value;
  if (!token) redirect("/login");

  const res = await fetch(
    `${process.env.API_URL ?? "http://localhost:8000"}/api/v1/auth/me`,
    {
      headers: { Cookie: `courtly_token=${token}` },
      cache: "no-store",
    },
  );
  if (!res.ok) redirect("/login");
  return res.json();
}

export default async function DashboardPage() {
  const { user, club } = await getDashboardData();
  const firstName = user.name.split(" ")[0];

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Olá, {firstName} 👋
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          {club
            ? `Gerenciando ${club.name}`
            : "Configure seu clube para começar"}
        </p>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Reservas hoje
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold tracking-tight">—</p>
            <p className="text-xs text-muted-foreground mt-1">
              Disponível após configurar quadras
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Quadras ativas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold tracking-tight">—</p>
            <p className="text-xs text-muted-foreground mt-1">
              Configure em <span className="text-foreground">Quadras</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Sua página de reservas
            </CardTitle>
          </CardHeader>
          <CardContent>
            {club ? (
              <>
                <p className="text-sm font-mono font-medium text-primary break-all">
                  /book/{club.slug}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Compartilhe com seus jogadores
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Não configurado</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Próximos passos */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-base">Próximos passos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>🎾 Adicione suas quadras para começar a receber reservas</p>
          <p>📅 Configure os horários de funcionamento do clube</p>
          <p>🔗 Compartilhe a página pública com seus jogadores</p>
        </CardContent>
      </Card>
    </div>
  );
}