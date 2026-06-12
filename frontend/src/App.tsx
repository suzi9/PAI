import { Navigate, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./auth";
import Login from "./pages/Login";
import Rejestracja from "./pages/Rejestracja";
import Salki from "./pages/Salki";
import SalkaSzczegoly from "./pages/SalkaSzczegoly";
import MojeRezerwacje from "./pages/MojeRezerwacje";
import Admin from "./pages/Admin";
import Publiczne from "./pages/Publiczne";

export default function App() {
  const { laduje } = useAuth();

  if (laduje) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-500">
        Ladowanie...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Publiczne />} />
          <Route path="/login" element={<Login />} />
          <Route path="/rejestracja" element={<Rejestracja />} />
          <Route
            path="/salki"
            element={
              <ProtectedRoute>
                <Salki />
              </ProtectedRoute>
            }
          />
          <Route
            path="/salki/:id"
            element={
              <ProtectedRoute>
                <SalkaSzczegoly />
              </ProtectedRoute>
            }
          />
          <Route
            path="/moje-rezerwacje"
            element={
              <ProtectedRoute>
                <MojeRezerwacje />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute rolaWymagana="admin">
                <Admin />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
