import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { api, tokenStorage, Uzytkownik } from "./api";

type AuthCtx = {
  uzytkownik: Uzytkownik | null;
  zalogowany: boolean;
  laduje: boolean;
  zaloguj: (email: string, haslo: string) => Promise<void>;
  wyloguj: () => void;
  odswiez: () => Promise<void>;
};

const AuthContext = createContext<AuthCtx | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [uzytkownik, setUzytkownik] = useState<Uzytkownik | null>(null);
  const [laduje, setLaduje] = useState(false);

  const odswiez = useCallback(async () => {
    try {
      const u = await api.ja();
      setUzytkownik(u);
    } catch {
      setUzytkownik(null);
    }
  }, []);

  useEffect(() => {
    odswiez();
  }, []);

  const zaloguj = useCallback(async (email: string, haslo: string) => {
    const { access_token } = await api.logowanie(email, haslo);
    tokenStorage.set(access_token);
  }, []);

  const wyloguj = useCallback(() => {
    tokenStorage.clear();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        uzytkownik,
        zalogowany: !!uzytkownik,
        laduje,
        zaloguj,
        wyloguj,
        odswiez,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("Brak kontekstu");
  return ctx;
}