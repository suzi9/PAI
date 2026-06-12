import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api, ApiError } from "../api";
import { useAuth } from "../auth";

export default function Rejestracja() {
  const { zaloguj } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [haslo, setHaslo] = useState("");
  const [imieNazwisko, setImieNazwisko] = useState("");
  const [blad, setBlad] = useState<string | null>(null);
  const [wysylanie, setWysylanie] = useState(false);

  const obslugaWyslania = async (e: FormEvent) => {
    e.preventDefault();
    setBlad(null);
    setWysylanie(true);
    try {
      await api.rejestracja({ email, haslo, imie_nazwisko: imieNazwisko });
      await zaloguj(email, haslo);
      navigate("/salki");
    } catch (err) {
      setBlad(err instanceof ApiError ? err.detail : "Blad rejestracji");
    } finally {
      setWysylanie(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-4">Rejestracja</h1>
      <form onSubmit={obslugaWyslania} className="flex flex-col gap-3">
        <label className="flex flex-col text-sm">
          Imie i nazwisko
          <input
            type="text"
            value={imieNazwisko}
            onChange={(e) => setImieNazwisko(e.target.value)}
            required
            minLength={2}
            className="mt-1 border border-gray-300 rounded px-3 py-2"
          />
        </label>
        <label className="flex flex-col text-sm">
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 border border-gray-300 rounded px-3 py-2"
          />
        </label>
        <label className="flex flex-col text-sm">
          Haslo (min. 6 znakow)
          <input
            type="password"
            value={haslo}
            onChange={(e) => setHaslo(e.target.value)}
            required
            minLength={6}
            className="mt-1 border border-gray-300 rounded px-3 py-2"
          />
        </label>
        {blad && <p className="text-red-600 text-sm">{blad}</p>}
        <button
          type="submit"
          disabled={wysylanie}
          className="bg-blue-600 text-white rounded py-2 font-medium hover:bg-blue-700 disabled:opacity-60"
        >
          {wysylanie ? "Wysylanie..." : "Zarejestruj sie"}
        </button>
      </form>
      <p className="text-sm mt-4 text-gray-600">
        Masz juz konto?{" "}
        <Link to="/login" className="text-blue-600 hover:underline">
          Zaloguj sie
        </Link>
      </p>
    </div>
  );
}
