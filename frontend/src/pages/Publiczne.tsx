import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { useAuth } from "../auth";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Wyposazenie = { id: number; nazwa: string };
type Salka = {
  id: number;
  nazwa: string;
  lokalizacja: string;
  pojemnosc: number;
  wyposazenie: Wyposazenie[];
};
type Rezerwacja = {
  salka_id: number;
  salka: string;
  lokalizacja: string;
  tytul: string;
  od: string;
  do: string;
};

function dzisISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function godzina(iso: string): string {
  return new Date(iso).toLocaleTimeString("pl-PL", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function tenSamDzien(iso: string, dzien: string): boolean {
  const d = new Date(iso);
  const local =
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
      d.getDate(),
    ).padStart(2, "0")}`;
  return local === dzien;
}

async function pobierzJSON<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) {
    const txt = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status} ${url} ${txt.slice(0, 200)}`);
  }
  return (await r.json()) as T;
}

export default function Publiczne() {
  const { zalogowany } = useAuth();
  const [dzien, setDzien] = useState<string>(dzisISO());

  const salkiQ = useQuery({
    queryKey: ["publiczne-salki"],
    queryFn: () => pobierzJSON<Salka[]>(`${API_URL}/publiczne/salki`),
  });

  const dostQ = useQuery({
    queryKey: ["publiczne-dostepnosc"],
    queryFn: () =>
      pobierzJSON<Rezerwacja[]>(`${API_URL}/publiczne/dostepnosc`),
  });

  const rezerwacjeDnia = useMemo(() => {
    const m = new Map<number, Rezerwacja[]>();
    for (const r of dostQ.data ?? []) {
      if (!tenSamDzien(r.od, dzien)) continue;
      const lista = m.get(r.salka_id) ?? [];
      lista.push(r);
      m.set(r.salka_id, lista);
    }
    for (const lista of m.values()) {
      lista.sort((a, b) => a.od.localeCompare(b.od));
    }
    return m;
  }, [dostQ.data, dzien]);

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold">Dostepnosc salek</h1>
            <p className="text-sm text-gray-600 mt-1">
              Wszystkie salki i ich zajetosc w wybranym dniu.
              {!zalogowany && (
                <>
                  {" "}Aby zarezerwowac {" "}
                  <Link to="/login" className="text-blue-600 hover:underline">
                    zaloguj sie
                  </Link>{" "}
                  lub{" "}
                  <Link
                    to="/rejestracja"
                    className="text-blue-600 hover:underline"
                  >
                    zarejestruj
                  </Link>
                  .
                </>
              )}
              {zalogowany && (
                <>
                  {" "}Przejdz do{" "}
                  <Link to="/salki" className="text-blue-600 hover:underline">
                    listy salek
                  </Link>{" "}
                  zeby zarezerwowac.
                </>
              )}
            </p>
          </div>
          <label className="flex items-center gap-2 text-sm">
            Dzien:
            <input
              type="date"
              value={dzien}
              onChange={(e) => setDzien(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2"
            />
          </label>
        </div>
      </div>

      {(salkiQ.isLoading || dostQ.isLoading) && (
        <p className="text-gray-500">Ladowanie...</p>
      )}

      {salkiQ.isError && (
        <div className="bg-red-50 text-red-800 p-4 rounded-lg shadow text-sm">
          Blad ladowania salek: {String((salkiQ.error as Error).message)}
        </div>
      )}
      {dostQ.isError && (
        <div className="bg-red-50 text-red-800 p-4 rounded-lg shadow text-sm">
          Blad ladowania rezerwacji:{" "}
          {String((dostQ.error as Error).message)}
        </div>
      )}

      {salkiQ.data && salkiQ.data.length === 0 && (
        <div className="bg-white p-6 rounded-lg shadow text-gray-500">
          Brak salek do wyswietlenia.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {(salkiQ.data ?? []).map((s) => {
          const slots = rezerwacjeDnia.get(s.id) ?? [];
          const wolna = slots.length === 0;
          return (
            <div key={s.id} className="bg-white p-5 rounded-lg shadow">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="text-lg font-semibold">{s.nazwa}</h3>
                  <p className="text-sm text-gray-600">{s.lokalizacja}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Pojemnosc: {s.pojemnosc}
                  </p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded font-medium whitespace-nowrap ${
                    wolna
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {wolna ? "Wolna" : `Zajeta (${slots.length})`}
                </span>
              </div>

              {s.wyposazenie.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {s.wyposazenie.map((w) => (
                    <span
                      key={w.id}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded"
                    >
                      {w.nazwa}
                    </span>
                  ))}
                </div>
              )}

              {!wolna && (
                <ul className="mt-3 space-y-1 text-sm">
                  {slots.map((r, i) => (
                    <li
                      key={i}
                      className="bg-red-50 text-red-800 px-3 py-1.5 rounded flex justify-between"
                    >
                      <span className="font-medium whitespace-nowrap">
                        {godzina(r.od)} – {godzina(r.do)}
                      </span>
                      <span className="text-red-600 text-xs truncate ml-2 max-w-[60%]">
                        {r.tytul}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {wolna && (
                <p className="mt-3 text-sm text-gray-500">
                  Brak rezerwacji w wybranym dniu.
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
