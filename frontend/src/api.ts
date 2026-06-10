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
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  let body = opts.body ? String(opts.body) : undefined;

  const res = await fetch(`${API_URL}${path}`, { ...opts, headers, body });

  const text = await res.text();
  const data = text ? text : null;

  if (!res.ok) {
    throw new ApiError(res.status, String(data));
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
  rejestracja: (dane: any) =>
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

  listaSalek: () => request<Salka[]>("/salki"),

  szczegolySalki: (id: number) => request<Salka>(`/salki/${id}`),

  utworzSalke: (dane: any) => request<Salka>("/salki", { method: "POST", body: dane }),

  edytujSalke: (id: number, dane: any) =>
    request<Salka>(`/salki/${id}`, { method: "PATCH", body: dane }),

  usunSalke: (id: number) => request<void>(`/salki/${id}`, { method: "DELETE" }),

  listaWyposazenia: () => request<Wyposazenie[]>("/wyposazenie"),

  utworzWyposazenie: (nazwa: string) =>
    request<Wyposazenie>("/wyposazenie", { method: "POST", body: { nazwa } }),

  usunWyposazenie: (id: number) =>
    request<void>(`/wyposazenie/${id}`, { method: "DELETE" }),

  mojeRezerwacje: () => request<Rezerwacja[]>("/rezerwacje/moje"),

  dostepnoscSalki: (salkaId: number, dzien: string) =>
    request<ZajetyPrzedzial[]>(`/rezerwacje/salka/${salkaId}/dostepnosc?dzien=${dzien}`),

  utworzRezerwacje: (dane: any) =>
    request<Rezerwacja>("/rezerwacje", { method: "POST", body: dane }),

  anulujRezerwacje: (id: number) =>
    request<void>(`/rezerwacje/${id}`, { method: "DELETE" }),
};