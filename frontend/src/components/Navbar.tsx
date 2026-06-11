import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";

export default function Navbar() {
  const { uzytkownik, zalogowany, wyloguj } = useAuth();
  const navigate = useNavigate();

  const obslugaWylogowania = () => {
    wyloguj();
    navigate("/login");
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium ${
      isActive ? "bg-blue-600 text-white" : "text-gray-700 hover:bg-gray-200"
    }`;

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-lg font-semibold text-gray-900">
          Roomly
        </Link>
        <nav className="flex items-center gap-2">
          <NavLink to="/" className={linkClass} end>
            Strona glowna
          </NavLink>
          {zalogowany ? (
            <>
              <NavLink to="/salki" className={linkClass}>
                Salki (rezerwuj)
              </NavLink>
              <NavLink to="/moje-rezerwacje" className={linkClass}>
                Moje rezerwacje
              </NavLink>
              {uzytkownik?.rola === "admin" && (
                <NavLink to="/admin" className={linkClass}>
                  Admin
                </NavLink>
              )}
              <span className="text-sm text-gray-500 px-2">
                {uzytkownik?.imie_nazwisko} ({uzytkownik?.rola})
              </span>
              <button
                onClick={obslugaWylogowania}
                className="px-3 py-2 rounded-md text-sm font-medium bg-gray-800 text-white hover:bg-gray-900"
              >
                Wyloguj
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Zaloguj
              </NavLink>
              <NavLink to="/rejestracja" className={linkClass}>
                Rejestracja
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
