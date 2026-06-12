import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiError } from "../api";

export default function Admin() {
  const qc = useQueryClient();
  const [bladSalka, setBladSalka] = useState<string | null>(null);
  const [bladWyp, setBladWyp] = useState<string | null>(null);

  const [nazwa, setNazwa] = useState("");
  const [pojemnosc, setPojemnosc] = useState<number>(4);
  const [lokalizacja, setLokalizacja] = useState("");
  const [wybraneWyp, setWybraneWyp] = useState<number[]>([]);
  const [nowaWypNazwa, setNowaWypNazwa] = useState("");

  const { data: salki } = useQuery({
    queryKey: ["admin-salki"],
    queryFn: () => api.listaSalek(),
  });
  const { data: wyposazenie } = useQuery({
    queryKey: ["wyposazenie"],
    queryFn: api.listaWyposazenia,
  });

  const mutDodajSalke = useMutation({
    mutationFn: api.utworzSalke,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-salki"] });
      qc.invalidateQueries({ queryKey: ["salki"] });
      setNazwa("");
      setPojemnosc(4);
      setLokalizacja("");
      setWybraneWyp([]);
      setBladSalka(null);
    },
    onError: (err) =>
      setBladSalka(err instanceof ApiError ? err.detail : "Blad tworzenia salki"),
  });

  const mutUsunSalke = useMutation({
    mutationFn: api.usunSalke,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-salki"] });
      qc.invalidateQueries({ queryKey: ["salki"] });
    },
  });

  const mutDodajWyp = useMutation({
    mutationFn: api.utworzWyposazenie,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["wyposazenie"] });
      setNowaWypNazwa("");
      setBladWyp(null);
    },
    onError: (err) =>
      setBladWyp(err instanceof ApiError ? err.detail : "Blad dodawania wyposazenia"),
  });

  const mutUsunWyp = useMutation({
    mutationFn: api.usunWyposazenie,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["wyposazenie"] });
      qc.invalidateQueries({ queryKey: ["admin-salki"] });
    },
  });

  const obslugaDodaniaSalki = (e: FormEvent) => {
    e.preventDefault();
    mutDodajSalke.mutate({
      nazwa,
      pojemnosc,
      lokalizacja,
      aktywna: true,
      wyposazenie_ids: wybraneWyp,
    });
  };

  const togglujWyp = (id: number) => {
    setWybraneWyp((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-3">Dodaj salke</h2>
        <form onSubmit={obslugaDodaniaSalki} className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Nazwa"
            value={nazwa}
            onChange={(e) => setNazwa(e.target.value)}
            required
            className="border border-gray-300 rounded px-3 py-2"
          />
          <input
            type="number"
            min={1}
            max={1000}
            placeholder="Pojemnosc"
            value={pojemnosc}
            onChange={(e) => setPojemnosc(Number(e.target.value))}
            required
            className="border border-gray-300 rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Lokalizacja"
            value={lokalizacja}
            onChange={(e) => setLokalizacja(e.target.value)}
            required
            className="border border-gray-300 rounded px-3 py-2"
          />
          <div>
            <p className="text-sm font-medium mb-1">Wyposazenie:</p>
            <div className="flex flex-wrap gap-2">
              {(wyposazenie ?? []).map((w) => (
                <label key={w.id} className="flex items-center gap-1 text-sm">
                  <input
                    type="checkbox"
                    checked={wybraneWyp.includes(w.id)}
                    onChange={() => togglujWyp(w.id)}
                  />
                  {w.nazwa}
                </label>
              ))}
            </div>
          </div>
          {bladSalka && <p className="text-red-600 text-sm">{bladSalka}</p>}
          <button
            type="submit"
            disabled={mutDodajSalke.isPending}
            className="bg-blue-600 text-white rounded py-2 font-medium hover:bg-blue-700 disabled:opacity-60"
          >
            Dodaj
          </button>
        </form>

        <h3 className="mt-6 font-semibold">Wszystkie salki</h3>
        <ul className="mt-2 divide-y">
          {(salki ?? []).map((s) => (
            <li key={s.id} className="py-2 flex items-center justify-between">
              <span className="text-sm">
                {s.nazwa} — {s.lokalizacja} (pojemnosc {s.pojemnosc})
              </span>
              <button
                onClick={() => mutUsunSalke.mutate(s.id)}
                className="text-red-600 hover:underline text-sm"
              >
                Usun
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-3">Wyposazenie</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutDodajWyp.mutate(nowaWypNazwa);
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            placeholder="Nazwa wyposazenia"
            value={nowaWypNazwa}
            onChange={(e) => setNowaWypNazwa(e.target.value)}
            required
            className="flex-1 border border-gray-300 rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={mutDodajWyp.isPending}
            className="bg-blue-600 text-white px-4 rounded font-medium hover:bg-blue-700 disabled:opacity-60"
          >
            Dodaj
          </button>
        </form>
        {bladWyp && <p className="text-red-600 text-sm mt-2">{bladWyp}</p>}

        <ul className="mt-4 divide-y">
          {(wyposazenie ?? []).map((w) => (
            <li key={w.id} className="py-2 flex items-center justify-between">
              <span className="text-sm">{w.nazwa}</span>
              <button
                onClick={() => mutUsunWyp.mutate(w.id)}
                className="text-red-600 hover:underline text-sm"
              >
                Usun
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
