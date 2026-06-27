import { redirect } from "next/navigation";

// A raiz redireciona para login.
// O middleware cuida de redirecionar para /admin/dashboard se já estiver autenticado.
export default function Home() {
  redirect("/login");
}