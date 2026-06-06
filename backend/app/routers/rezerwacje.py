from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, wymagaj_admina
from app.models import Rezerwacja, Salka, Uzytkownik
from app.schemas import RezerwacjaIn, RezerwacjaOdp, ZajetyPrzedzial

router = APIRouter(prefix="/rezerwacje", tags=["rezerwacje"])

MIN_DLUGOSC = timedelta(minutes=15)
MAX_DLUGOSC = timedelta(hours=8)


def _waliduj_okno(od: datetime, do_: datetime) -> None:
    if od.tzinfo is None or do_.tzinfo is None:
        raise HTTPException(
            status_code=400,
            detail="Daty musza zawierac strefe czasowa (ISO 8601 z offsetem)",
        )
    if od >= do_:
        raise HTTPException(status_code=400, detail="'od' musi byc przed 'do'")
    dlugosc = do_ - od
    if dlugosc < MIN_DLUGOSC:
        raise HTTPException(status_code=400, detail="Rezerwacja krotsza niz 15 minut")
    if dlugosc > MAX_DLUGOSC:
        raise HTTPException(status_code=400, detail="Rezerwacja dluzsza niz 8 godzin")
    if od < datetime.now(tz=timezone.utc):
        raise HTTPException(status_code=400, detail="Nie mozna rezerwowac w przeszlosci")


async def _sprawdz_kolizje(
    session: AsyncSession,
    salka_id: int,
    od: datetime,
    do_: datetime,
    pomin_id: int | None = None,
) -> None:
    stmt = select(Rezerwacja).where(
        and_(
            Rezerwacja.salka_id == salka_id,
            Rezerwacja.status == "aktywna",
            Rezerwacja.od < do_,
            Rezerwacja.do_ > od,
        )
    )
    if pomin_id is not None:
        stmt = stmt.where(Rezerwacja.id != pomin_id)
    res = await session.execute(stmt)
    if res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Salka jest juz zarezerwowana w tym oknie czasowym",
        )


@router.get("/moje", response_model=list[RezerwacjaOdp])
async def moje_rezerwacje(
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Rezerwacja]:
    res = await session.execute(
        select(Rezerwacja)
        .where(Rezerwacja.uzytkownik_id == uzytkownik.id)
        .order_by(Rezerwacja.od.desc())
    )
    return list(res.scalars().all())


@router.get("", response_model=list[RezerwacjaOdp])
async def wszystkie_rezerwacje(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> list[Rezerwacja]:
    res = await session.execute(select(Rezerwacja).order_by(Rezerwacja.od.desc()))
    return list(res.scalars().all())


@router.get("/salka/{salka_id}/dostepnosc", response_model=list[ZajetyPrzedzial])
async def dostepnosc_salki(
    salka_id: int,
    dzien: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(get_current_user),
) -> list[ZajetyPrzedzial]:
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Salka nie istnieje")

    poczatek = datetime.combine(dzien, time.min, tzinfo=timezone.utc)
    koniec = datetime.combine(dzien, time.max, tzinfo=timezone.utc)
    stmt = (
        select(Rezerwacja)
        .where(
            and_(
                Rezerwacja.salka_id == salka_id,
                Rezerwacja.status == "aktywna",
                or_(
                    and_(Rezerwacja.od >= poczatek, Rezerwacja.od <= koniec),
                    and_(Rezerwacja.do_ >= poczatek, Rezerwacja.do_ <= koniec),
                ),
            )
        )
        .order_by(Rezerwacja.od)
    )
    res = await session.execute(stmt)
    return [ZajetyPrzedzial(od=r.od, do_=r.do_) for r in res.scalars().all()]


@router.post("", response_model=RezerwacjaOdp, status_code=status.HTTP_201_CREATED)
async def utworz_rezerwacje(
    dane: RezerwacjaIn,
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Rezerwacja:
    _waliduj_okno(dane.od, dane.do_)

    res = await session.execute(select(Salka).where(Salka.id == dane.salka_id))
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Salka nie istnieje")
    if not salka.aktywna:
        raise HTTPException(status_code=400, detail="Salka jest nieaktywna")

    await _sprawdz_kolizje(session, dane.salka_id, dane.od, dane.do_)

    rezerwacja = Rezerwacja(
        uzytkownik_id=uzytkownik.id,
        salka_id=dane.salka_id,
        tytul=dane.tytul,
        od=dane.od,
        do_=dane.do_,
        status="aktywna",
    )
    session.add(rezerwacja)
    await session.commit()
    await session.refresh(rezerwacja)
    return rezerwacja


@router.delete("/{rezerwacja_id}", status_code=status.HTTP_204_NO_CONTENT)
async def anuluj_rezerwacje(
    rezerwacja_id: int,
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    res = await session.execute(
        select(Rezerwacja).where(Rezerwacja.id == rezerwacja_id)
    )
    rezerwacja = res.scalar_one_or_none()
    if rezerwacja is None:
        raise HTTPException(status_code=404, detail="Rezerwacja nie istnieje")
    if rezerwacja.uzytkownik_id != uzytkownik.id and uzytkownik.rola != "admin":
        raise HTTPException(status_code=403, detail="Brak uprawnien")
    rezerwacja.status = "anulowana"
    await session.commit()
