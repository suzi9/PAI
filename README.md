# Roomly— System rezerwacji salek konferencyjnych

Aplikacja webowa do rezerwowania salek konferencyjnych w firmie. 

## Realizacja wymagan

| ID | Wymaganie | Realizacja |
|----|-----------|------------|
| R1 | Backend API z min. 4 zasobami w relacjach | REST API (FastAPI) z 4 zasobami: `Uzytkownik`, `Salka`, `Wyposazenie`, `Rezerwacja` |
| R2 | Baza danych z migracjami | PostgreSQL 16 + Alembic |
| R3 | Frontend komunikujacy sie z API | SPA w React 18 + Vite + TypeScript |
| R4 | Autentykacja z ochrona endpointow | JWT (access token) + role `admin` / `user` |
| R5 | Konteneryzacja (`docker-compose`) | 4 serwisy: db, adminer, backend, frontend — `docker compose up --build` |


## Stack technologiczny

**Backend**: Python 3.12, FastAPI 0.115, SQLAlchemy 2.0 (async), Alembic, asyncpg, Pydantic v2, python-jose (JWT), passlib[bcrypt].

**Frontend**: React 18, TypeScript, Vite 5, TanStack Query 5, React Router 6, Tailwind CSS 3.

**Baza danych**: PostgreSQL 16.

**Konteneryzacja**: Docker + Docker Compose v2.

## Model domeny

```
Uzytkownik ──1:N──► Rezerwacja ◄──N:1── Salka ──N:M──► Wyposazenie
```

| Encja | Pola | Relacje |
|-------|------|---------|
| `Uzytkownik` | id, email, haslo_hash, imie_nazwisko, rola, utworzono | 1:N → `Rezerwacja` |
| `Salka` | id, nazwa, pojemnosc, lokalizacja, aktywna, utworzono | 1:N → `Rezerwacja`; N:M → `Wyposazenie` |
| `Wyposazenie` | id, nazwa | N:M → `Salka` |
| `Rezerwacja` | id, uzytkownik_id, salka_id, tytul, od, do, status, utworzono | N:1 → `Uzytkownik`, `Salka` |

Tabela laczaca: `salka_wyposazenie(salka_id, wyposazenie_id)`.

**Reguly biznesowe rezerwacji:**
- Czas trwania: min. 15 minut, max. 8 godzin.
- Nie mozna rezerwowac w przeszlosci.
- Nie mozna nakladac rezerwacji na te sama salke (walidacja w `_sprawdz_kolizje`).
- Anulowanie = `status='anulowana'` (soft delete).

## Uruchomienie

Wymagania: zainstalowany **Docker** i **Docker Compose v2**.

```bash
git clone https://github.com/suzi9/PAI.git
cd PAI
cp .env.example .env
docker compose up --build
```

Po podniesieniu sie wszystkich serwisow:

| Serwis | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| API + Swagger UI | http://localhost:8000/docs |
| Adminer (podglad bazy) | http://localhost:8080 |

Skroty (Makefile):

```bash
make up         # uruchom serwisy w tle
make up-build   # przebuduj i uruchom
make down       # zatrzymaj
make logs       # logi (follow)
make ps         # status kontenerow
make psql       # konsola psql na bazie
make seed       # zaladuj dane testowe (admin + uzytkownik + 5 salek)
make clean      # zatrzymaj i usun wolumeny (kasuje dane)
```

## Dane testowe (seed)

Po uruchomieniu aplikacji wykonaj:

```bash
make seed
```

Utworzy:

| Konto | Email | Haslo | Rola |
|-------|-------|-------|------|
| Administrator | `admin@pai.local` | `admin123` | `admin` |
| Uzytkownik | `user@pai.local` | `user123` | `user` |

Oraz 5 przykladowych salek z wyposazeniem (Projektor, Telewizor, Tablica, Klimatyzacja, Telekonferencja).

## Endpointy API

Pelna dokumentacja interaktywna pod `http://localhost:8000/docs` (Swagger UI generowany automatycznie przez FastAPI).

## Autentykacja

1. Uzytkownik wysyla `POST /auth/rejestracja` z `email`, `haslo`, `imie_nazwisko`. Domyslna rola: `user`.
2. Logowanie: `POST /auth/logowanie` (form `username=email`, `password=haslo`). Backend zwraca `{ access_token, token_type }`.
3. Frontend zapisuje token w `localStorage` i dolacza w naglowku `Authorization: Bearer <token>`.
4. Backend dekoduje token przez `python-jose`, weryfikuje podpis HS256, wyciaga `sub` (id uzytkownika) i `rola`, laduje uzytkownika z DB.
5. Endpointy admina (`POST /salki`, `POST /wyposazenie`, `GET /rezerwacje`) maja zaleznosc `wymagaj_admina`, ktora odrzuca rola `user` z HTTP 403.
6. Po wygasnieciu tokenu (60 min) backend zwraca 401, frontend czysci `localStorage` i przekierowuje na `/login`.
