const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "pai_token";

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

type FetchOpts = RequestInit & { body?: unknown };

async function request<T>(path: string, opts: FetchOpts = {}): Promise<T> {
  const token = tokenStorage.get();
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(opts.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let body = opts.body as BodyInit | undefined;
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body !== "string") {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  const res = await fetch(`${API_URL}${path}`, { ...opts, headers, body });

  if (res.status === 204) return undefined as T;

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      (data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : null) ?? `HTTP ${res.status}`;
    if (res.status === 401) tokenStorage.clear();
    throw new ApiError(res.status, detail);
  }

  return data as T;
}

export type Uzytkownik = {
  id: number;
  email: string;
  imie_nazwisko: string;
  rola: "admin" | "user";
  utworzono: string;
};

export type Wyposazenie = { id: number; nazwa: string };

export type Salka = {
  id: number;
  nazwa: string;
  pojemnosc: number;
  lokalizacja: string;
  aktywna: boolean;
  wyposazenie: Wyposazenie[];
};

export type Rezerwacja = {
  id: number;
  salka_id: number;
  uzytkownik_id: number;
  tytul: string;
  od: string;
  do: string;
  status: "aktywna" | "anulowana";
  utworzono: string;
};

export type ZajetyPrzedzial = { od: string; do: string };

export const api = {
  rejestracja: (dane: { email: string; haslo: string; imie_nazwisko: string }) =>
    request<Uzytkownik>("/auth/rejestracja", { method: "POST", body: dane }),

  logowanie: async (email: string, haslo: string) => {
    const form = new FormData();
    form.append("username", email);
    form.append("password", haslo);
    return request<{ access_token: string; token_type: string }>("/auth/logowanie", {
      method: "POST",
      body: form,
    });
  },

  ja: () => request<Uzytkownik>("/auth/ja"),

  listaSalek: (params: { pojemnoscMin?: number; wyposazenieId?: number[] } = {}) => {
    const q = new URLSearchParams();
    if (params.pojemnoscMin) q.append("pojemnosc_min", String(params.pojemnoscMin));
    (params.wyposazenieId ?? []).forEach((id) =>
      q.append("wyposazenie_id", String(id)),
    );
    const qs = q.toString();
    return request<Salka[]>(`/salki${qs ? `?${qs}` : ""}`);
  },

  szczegolySalki: (id: number) => request<Salka>(`/salki/${id}`),

  utworzSalke: (dane: {
    nazwa: string;
    pojemnosc: number;
    lokalizacja: string;
    aktywna: boolean;
    wyposazenie_ids: number[];
  }) => request<Salka>("/salki", { method: "POST", body: dane }),

  edytujSalke: (
    id: number,
    dane: Partial<{
      nazwa: string;
      pojemnosc: number;
      lokalizacja: string;
      aktywna: boolean;
      wyposazenie_ids: number[];
    }>,
  ) => request<Salka>(`/salki/${id}`, { method: "PATCH", body: dane }),

  usunSalke: (id: number) => request<void>(`/salki/${id}`, { method: "DELETE" }),

  listaWyposazenia: () => request<Wyposazenie[]>("/wyposazenie"),

  utworzWyposazenie: (nazwa: string) =>
    request<Wyposazenie>("/wyposazenie", { method: "POST", body: { nazwa } }),

  usunWyposazenie: (id: number) =>
    request<void>(`/wyposazenie/${id}`, { method: "DELETE" }),

  mojeRezerwacje: () => request<Rezerwacja[]>("/rezerwacje/moje"),

  dostepnoscSalki: (salkaId: number, dzien: string) =>
    request<ZajetyPrzedzial[]>(`/rezerwacje/salka/${salkaId}/dostepnosc?dzien=${dzien}`),

  utworzRezerwacje: (dane: {
    salka_id: number;
    tytul: string;
    od: string;
    do: string;
  }) => request<Rezerwacja>("/rezerwacje", { method: "POST", body: dane }),

  anulujRezerwacje: (id: number) =>
    request<void>(`/rezerwacje/${id}`, { method: "DELETE" }),
};