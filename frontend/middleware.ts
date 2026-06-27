import { NextRequest, NextResponse } from "next/server";

const COOKIE_NAME = "courtly_token";
const ADMIN_PREFIX = "/admin";
const AUTH_ROUTES = new Set(["/login", "/register"]);
const PUBLIC_PREFIXES = ["/book", "/api", "/_next", "/favicon"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Deixar passar: assets, proxy de API, rotas públicas de reserva
  if (PUBLIC_PREFIXES.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const token = request.cookies.get(COOKIE_NAME)?.value;

  // Rota protegida sem token → redireciona para login
  if (pathname.startsWith(ADMIN_PREFIX) && !token) {
    const url = new URL("/login", request.url);
    url.searchParams.set("from", pathname); // preserva destino para redirecionar após login
    return NextResponse.redirect(url);
  }

  // Rota de auth com token → já está logado, vai para o dashboard
  if (AUTH_ROUTES.has(pathname) && token) {
    return NextResponse.redirect(new URL("/admin/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Aplica o middleware em todas as rotas exceto arquivos estáticos
  matcher: ["/((?!_next/static|_next/image|favicon\\.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};