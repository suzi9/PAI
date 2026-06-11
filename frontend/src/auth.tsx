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
  const [laduje, setLaduje] = useState(true);

  const odswiez = useCallback(async () => {
    if (!tokenStorage.get()) {
      setUzytkownik(null);
      setLaduje(false);
      return;
    }
    try {
      const u = await api.ja();
      setUzytkownik(u);
    } catch {
      tokenStorage.clear();
      setUzytkownik(null);
    } finally {
      setLaduje(false);
    }
  }, []);

  useEffect(() => {
    odswiez();
  }, [odswiez]);

  const zaloguj = useCallback(
    async (email: string, haslo: string) => {
      const { access_token } = await api.logowanie(email, haslo);
      tokenStorage.set(access_token);
      await odswiez();
    },
    [odswiez],
  );

  const wyloguj = useCallback(() => {
    tokenStorage.clear();
    setUzytkownik(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        uzytkownik,
        zalogowany: uzytkownik !== null,
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
  if (!ctx) throw new Error("useAuth musi byc wewnatrz AuthProvider");
  return ctx;
}