import type { MeResponse, RegisterPayload } from "./types";

// Prefixo usado por Client Components (vai pelo proxy de rewrites do Next.js)
const API = "/api/v1";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    credentials: "include", // envia o cookie httpOnly automaticamente
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Erro na requisição." }));
    throw new ApiError(res.status, body.detail ?? "Erro desconhecido.");
  }

  // Respostas sem body (ex: 204 No Content)
  const text = await res.text();
  return text ? (JSON.parse(text) as T) : (undefined as T);
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    request<MeResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (email: string, password: string) =>
    request<{ message: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    request<{ message: string }>("/auth/logout", { method: "POST" }),

  me: () => request<MeResponse>("/auth/me"),
};