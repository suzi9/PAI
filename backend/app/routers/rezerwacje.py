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
    if od >= do_:
        raise HTTPException(status_code=400, detail="'od' musi byc przed 'do'")
    if do_ - od < MIN_DLUGOSC:
        raise HTTPException(status_code=400, detail="Rezerwacja krotsza niz 15 minut")


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
            Rezerwacja.od < do_,
            Rezerwacja.do_ > od,
        )
    )
    res = await session.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Kolizja")


@router.get("/moje", response_model=list[RezerwacjaOdp])
async def moje_rezerwacje(
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Rezerwacja]:
    res = await session.execute(
        select(Rezerwacja).where(Rezerwacja.uzytkownik_id == uzytkownik.id)
    )
    return res.scalars().all()


@router.get("", response_model=list[RezerwacjaOdp])
async def wszystkie_rezerwacje(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> list[Rezerwacja]:
    res = await session.execute(select(Rezerwacja))
    return res.scalars().all()


@router.get("/salka/{salka_id}/dostepnosc", response_model=list[ZajetyPrzedzial])
async def dostepnosc_salki(
    salka_id: int,
    dzien: date = Query(...),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(get_current_user),
) -> list[ZajetyPrzedzial]:
    poczatek = datetime.combine(dzien, time.min, tzinfo=timezone.utc)
    koniec = datetime.combine(dzien, time.max, tzinfo=timezone.utc)
    stmt = select(Rezerwacja).where(Rezerwacja.salka_id == salka_id)
    res = await session.execute(stmt)
    return [ZajetyPrzedzial(od=r.od, do_=r.do_) for r in res.scalars().all()]


@router.post("", response_model=RezerwacjaOdp, status_code=status.HTTP_201_CREATED)
async def utworz_rezerwacje(
    dane: RezerwacjaIn,
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Rezerwacja:
    _waliduj_okno(dane.od, dane.do_)
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
    return rezerwacja


@router.delete("/{rezerwacja_id}", status_code=status.HTTP_204_NO_CONTENT)
async def anuluj_rezerwacje(
    rezerwacja_id: int,
    uzytkownik: Uzytkownik = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    res = await session.execute(select(Rezerwacja).where(Rezerwacja.id == rezerwacja_id))
    rezerwacja = res.scalar_one_or_none()
    if rezerwacja is None:
        raise HTTPException(status_code=404, detail="Rezerwacja nie istnieje")
    rezerwacja.status = "anulowana"
    await session.commit()