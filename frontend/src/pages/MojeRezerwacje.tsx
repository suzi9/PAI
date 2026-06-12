import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../api";

function formatDT(iso: string): string {
  return new Date(iso).toLocaleString("pl-PL", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export default function MojeRezerwacje() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["moje-rezerwacje"],
    queryFn: api.mojeRezerwacje,
  });

  const anuluj = useMutation({
    mutationFn: api.anulujRezerwacje,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["moje-rezerwacje"] }),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Moje rezerwacje</h1>
      {isLoading && <p className="text-gray-500">Ladowanie...</p>}
      {data && data.length === 0 && (
        <p className="text-gray-500">Nie masz jeszcze zadnych rezerwacji.</p>
      )}
      <div className="bg-white rounded-lg shadow divide-y">
        {(data ?? []).map((r) => (
          <div key={r.id} className="p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold">{r.tytul}</p>
              <p className="text-sm text-gray-600">
                {formatDT(r.od)} → {formatDT(r.do)}
              </p>
              <p className="text-xs mt-1">
                <span
                  className={`px-2 py-0.5 rounded ${
                    r.status === "aktywna"
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {r.status}
                </span>
              </p>
            </div>
            {r.status === "aktywna" && (
              <button
                onClick={() => anuluj.mutate(r.id)}
                disabled={anuluj.isPending}
                className="bg-red-600 text-white text-sm px-3 py-1.5 rounded hover:bg-red-700 disabled:opacity-60"
              >
                Anuluj
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
