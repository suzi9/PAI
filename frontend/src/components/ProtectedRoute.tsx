import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../auth";

export default function ProtectedRoute({
  children,
  rolaWymagana,
}: {
  children: ReactNode;
  rolaWymagana?: "admin" | "user";
}) {
  const { zalogowany, uzytkownik } = useAuth();
  const location = useLocation();

  if (!zalogowany) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  if (rolaWymagana && uzytkownik?.rola !== rolaWymagana) {
    return (
      <div className="p-6 text-center text-red-600">
        Brak uprawnien. Wymagana rola: {rolaWymagana}.
      </div>
    );
  }
  return <>{children}</>;
}
