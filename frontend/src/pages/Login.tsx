import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";
import { ApiError } from "../api";

export default function Login() {
  const { zaloguj } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [haslo, setHaslo] = useState("");
  const [blad, setBlad] = useState<string | null>(null);
  const [wysylanie, setWysylanie] = useState(false);

  const obslugaWyslania = async (e: FormEvent) => {
    e.preventDefault();
    setBlad(null);
    setWysylanie(true);
    try {
      await zaloguj(email, haslo);
      navigate("/salki");
    } catch (err) {
      setBlad(err instanceof ApiError ? err.detail : "Blad logowania");
    } finally {
      setWysylanie(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-4">Logowanie</h1>
      <form onSubmit={obslugaWyslania} className="flex flex-col gap-3">
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
          Haslo
          <input
            type="password"
            value={haslo}
            onChange={(e) => setHaslo(e.target.value)}
            required
            className="mt-1 border border-gray-300 rounded px-3 py-2"
          />
        </label>
        {blad && <p className="text-red-600 text-sm">{blad}</p>}
        <button
          type="submit"
          disabled={wysylanie}
          className="bg-blue-600 text-white rounded py-2 font-medium hover:bg-blue-700 disabled:opacity-60"
        >
          {wysylanie ? "Logowanie..." : "Zaloguj"}
        </button>
      </form>
      <p className="text-sm mt-4 text-gray-600">
        Nie masz konta?{" "}
        <Link to="/rejestracja" className="text-blue-600 hover:underline">
          Zarejestruj sie
        </Link>
      </p>
      <p className="text-sm mt-2 text-gray-600">
        Albo{" "}
        <Link to="/" className="text-blue-600 hover:underline">
          wroc do publicznej listy salek
        </Link>
        .
      </p>
    </div>
  );
}