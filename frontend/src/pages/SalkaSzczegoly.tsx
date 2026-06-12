import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { api, ApiError } from "../api";

function dzisISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function lokalnaDoUTC(value: string): string {
  return new Date(value).toISOString();
}

function formatGodzina(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
}

export default function SalkaSzczegoly() {
  const { id } = useParams();
  const salkaId = Number(id);
  const qc = useQueryClient();

  const [dzien, setDzien] = useState<string>(dzisISO());
  const [tytul, setTytul] = useState("");
  const [od, setOd] = useState("");
  const [doCzasu, setDoCzasu] = useState("");
  const [blad, setBlad] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const { data: salka } = useQuery({
    queryKey: ["salka", salkaId],
    queryFn: () => api.szczegolySalki(salkaId),
    enabled: !Number.isNaN(salkaId),
  });

  const { data: zajete } = useQuery({
    queryKey: ["dostepnosc", salkaId, dzien],
    queryFn: () => api.dostepnoscSalki(salkaId, dzien),
    enabled: !Number.isNaN(salkaId),
  });

  const mutacja = useMutation({
    mutationFn: api.utworzRezerwacje,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dostepnosc", salkaId] });
      qc.invalidateQueries({ queryKey: ["moje-rezerwacje"] });
      setTytul("");
      setOd("");
      setDoCzasu("");
      setInfo("Rezerwacja utworzona.");
      setBlad(null);
    },
    onError: (err) => {
      setBlad(err instanceof ApiError ? err.detail : "Blad podczas tworzenia rezerwacji");
      setInfo(null);
    },
  });

  const obslugaWyslania = (e: FormEvent) => {
    e.preventDefault();
    setBlad(null);
    setInfo(null);
    mutacja.mutate({
      salka_id: salkaId,
      tytul,
      od: lokalnaDoUTC(od),
      do: lokalnaDoUTC(doCzasu),
    });
  };

  if (!salka) return <p className="text-gray-500">Ladowanie...</p>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold">{salka.nazwa}</h1>
        <p className="text-gray-600 mt-1">{salka.lokalizacja}</p>
        <p className="mt-2">Pojemnosc: {salka.pojemnosc}</p>
        <div className="mt-3 flex flex-wrap gap-1">
          {salka.wyposazenie.map((w) => (
            <span
              key={w.id}
              className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded"
            >
              {w.nazwa}
            </span>
          ))}
        </div>

        <h2 className="mt-6 font-semibold">Zajete przedzialy</h2>
        <label className="block text-sm mt-2">
          Dzien
          <input
            type="date"
            value={dzien}
            onChange={(e) => setDzien(e.target.value)}
            className="ml-2 border border-gray-300 rounded px-2 py-1"
          />
        </label>
        <ul className="mt-3 space-y-1 text-sm">
          {(zajete ?? []).length === 0 && (
            <li className="text-gray-500">Brak rezerwacji w wybranym dniu.</li>
          )}
          {(zajete ?? []).map((p, i) => (
            <li key={i} className="bg-red-50 text-red-700 px-3 py-1 rounded">
              {formatGodzina(p.od)} – {formatGodzina(p.do)}
            </li>
          ))}
        </ul>
      </section>

      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-3">Nowa rezerwacja</h2>
        <form onSubmit={obslugaWyslania} className="flex flex-col gap-3">
          <label className="flex flex-col text-sm">
            Tytul spotkania
            <input
              type="text"
              value={tytul}
              onChange={(e) => setTytul(e.target.value)}
              required
              maxLength={255}
              className="mt-1 border border-gray-300 rounded px-3 py-2"
            />
          </label>
          <label className="flex flex-col text-sm">
            Od
            <input
              type="datetime-local"
              value={od}
              onChange={(e) => setOd(e.target.value)}
              required
              className="mt-1 border border-gray-300 rounded px-3 py-2"
            />
          </label>
          <label className="flex flex-col text-sm">
            Do
            <input
              type="datetime-local"
              value={doCzasu}
              onChange={(e) => setDoCzasu(e.target.value)}
              required
              className="mt-1 border border-gray-300 rounded px-3 py-2"
            />
          </label>
          {blad && <p className="text-red-600 text-sm">{blad}</p>}
          {info && <p className="text-green-600 text-sm">{info}</p>}
          <button
            type="submit"
            disabled={mutacja.isPending}
            className="bg-blue-600 text-white rounded py-2 font-medium hover:bg-blue-700 disabled:opacity-60"
          >
            {mutacja.isPending ? "Rezerwowanie..." : "Zarezerwuj"}
          </button>
        </form>
      </section>
    </div>
  );
}
