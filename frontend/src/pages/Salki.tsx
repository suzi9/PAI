import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { api } from "../api";

export default function Salki() {
  const [pojemnoscMin, setPojemnoscMin] = useState<number | "">("");
  const [wybraneWyp, setWybraneWyp] = useState<number[]>([]);

  const { data: wyposazenie } = useQuery({
    queryKey: ["wyposazenie"],
    queryFn: api.listaWyposazenia,
  });

  const { data: salki, isLoading } = useQuery({
    queryKey: ["salki", pojemnoscMin, wybraneWyp],
    queryFn: () =>
      api.listaSalek({
        pojemnoscMin: pojemnoscMin === "" ? undefined : Number(pojemnoscMin),
        wyposazenieId: wybraneWyp.length ? wybraneWyp : undefined,
      }),
  });

  const togglujWyp = (id: number) => {
    setWybraneWyp((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[260px,1fr] gap-6">
      <aside className="bg-white p-4 rounded-lg shadow h-fit">
        <h2 className="font-semibold mb-3">Filtry</h2>
        <label className="block text-sm mb-3">
          Min. pojemnosc
          <input
            type="number"
            min={1}
            value={pojemnoscMin}
            onChange={(e) =>
              setPojemnoscMin(e.target.value === "" ? "" : Number(e.target.value))
            }
            className="mt-1 w-full border border-gray-300 rounded px-2 py-1"
          />
        </label>
        <div className="text-sm font-medium mb-2">Wyposazenie</div>
        <div className="flex flex-col gap-1">
          {(wyposazenie ?? []).map((w) => (
            <label key={w.id} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={wybraneWyp.includes(w.id)}
                onChange={() => togglujWyp(w.id)}
              />
              {w.nazwa}
            </label>
          ))}
        </div>
      </aside>

      <section>
        <h1 className="text-2xl font-bold mb-4">Dostepne salki</h1>
        {isLoading && <p className="text-gray-500">Ladowanie...</p>}
        {salki && salki.length === 0 && (
          <p className="text-gray-500">Brak salek spelniajacych kryteria.</p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(salki ?? []).map((s) => (
            <Link
              key={s.id}
              to={`/salki/${s.id}`}
              className="bg-white rounded-lg shadow p-4 hover:shadow-md transition"
            >
              <h3 className="text-lg font-semibold">{s.nazwa}</h3>
              <p className="text-sm text-gray-600">{s.lokalizacja}</p>
              <p className="text-sm mt-1">Pojemnosc: {s.pojemnosc}</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {s.wyposazenie.map((w) => (
                  <span
                    key={w.id}
                    className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded"
                  >
                    {w.nazwa}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
