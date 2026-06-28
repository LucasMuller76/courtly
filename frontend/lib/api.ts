import type { Court, MeResponse, RegisterPayload } from "./types";

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
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Erro na requisição." }));
    throw new ApiError(res.status, body.detail ?? "Erro desconhecido.");
  }

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

export const courtsApi = {
  list: () => request<Court[]>("/courts"),

  create: (data: Pick<Court, "name" | "price_per_hour">) =>
    request<Court>("/courts/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Partial<Pick<Court, "name" | "price_per_hour" | "is_active">>) =>
    request<Court>(`/courts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    request<void>(`/courts/${id}`, { method: "DELETE" }),
};