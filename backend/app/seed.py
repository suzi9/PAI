import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Salka, Uzytkownik, Wyposazenie
from app.security import hash_hasla


SEED_ADMIN_EMAIL = "admin@pai.local"
SEED_ADMIN_HASLO = "admin123"
SEED_USER_EMAIL = "user@pai.local"
SEED_USER_HASLO = "user123"


async def main() -> None:
    async with SessionLocal() as session:
        if (
            await session.execute(select(Uzytkownik).where(Uzytkownik.email == SEED_ADMIN_EMAIL))
        ).scalar_one_or_none() is None:
            session.add(
                Uzytkownik(
                    email=SEED_ADMIN_EMAIL,
                    haslo_hash=hash_hasla(SEED_ADMIN_HASLO),
                    imie_nazwisko="Administrator",
                    rola="admin",
                )
            )
        if (
            await session.execute(select(Uzytkownik).where(Uzytkownik.email == SEED_USER_EMAIL))
        ).scalar_one_or_none() is None:
            session.add(
                Uzytkownik(
                    email=SEED_USER_EMAIL,
                    haslo_hash=hash_hasla(SEED_USER_HASLO),
                    imie_nazwisko="Jan Pracownik",
                    rola="user",
                )
            )

        wyposazenie_nazwy = ["Projektor", "Telewizor", "Tablica", "Klimatyzacja", "Telekonferencja"]
        wyp_obj: dict[str, Wyposazenie] = {}
        for nazwa in wyposazenie_nazwy:
            istniejace = (
                await session.execute(select(Wyposazenie).where(Wyposazenie.nazwa == nazwa))
            ).scalar_one_or_none()
            if istniejace is None:
                w = Wyposazenie(nazwa=nazwa)
                session.add(w)
                wyp_obj[nazwa] = w
            else:
                wyp_obj[nazwa] = istniejace

        await session.flush()

        salki_def = [
            ("Sala Konferencyjna A", 12, "Pietro 1, pokoj 101", ["Projektor", "Tablica"]),
            ("Sala Spotkan B", 6, "Pietro 1, pokoj 102", ["Telewizor"]),
            ("Sala Warsztatowa C", 20, "Pietro 2, pokoj 201", ["Projektor", "Tablica", "Klimatyzacja"]),
            ("Boks Telefoniczny D", 2, "Pietro 2, korytarz", []),
            ("Sala Zarzadu E", 10, "Pietro 3, pokoj 301", ["Telewizor", "Telekonferencja", "Klimatyzacja"]),
        ]
        for nazwa, pojemnosc, lokalizacja, wyp_nazwy in salki_def:
            istniejaca = (
                await session.execute(select(Salka).where(Salka.nazwa == nazwa))
            ).scalar_one_or_none()
            if istniejaca is None:
                session.add(
                    Salka(
                        nazwa=nazwa,
                        pojemnosc=pojemnosc,
                        lokalizacja=lokalizacja,
                        aktywna=True,
                        wyposazenie=[wyp_obj[n] for n in wyp_nazwy],
                    )
                )

        await session.commit()
        print("Seed zakonczony.")
        print(f"  Admin: {SEED_ADMIN_EMAIL} / {SEED_ADMIN_HASLO}")
        print(f"  User:  {SEED_USER_EMAIL} / {SEED_USER_HASLO}")


if __name__ == "__main__":
    asyncio.run(main())
