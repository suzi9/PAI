from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user, wymagaj_admina
from app.models import Salka, Wyposazenie
from app.schemas import SalkaIn, SalkaOdp, SalkaUpdate

router = APIRouter(prefix="/salki", tags=["salki"])


async def _pobierz_wyposazenie(
    session: AsyncSession, ids: list[int]
) -> list[Wyposazenie]:
    if not ids:
        return []
    res = await session.execute(select(Wyposazenie).where(Wyposazenie.id.in_(ids)))
    znalezione = res.scalars().all()
    if len(znalezione) != len(set(ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niektore identyfikatory wyposazenia nie istnieja",
        )
    return list(znalezione)


@router.get("", response_model=list[SalkaOdp])
async def lista_salek(
    pojemnosc_min: int | None = Query(default=None, ge=1),
    wyposazenie_id: list[int] | None = Query(default=None),
    tylko_aktywne: bool = Query(default=True),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(get_current_user),
) -> list[Salka]:
    stmt = select(Salka).options(selectinload(Salka.wyposazenie))
    if tylko_aktywne:
        stmt = stmt.where(Salka.aktywna.is_(True))
    if pojemnosc_min is not None:
        stmt = stmt.where(Salka.pojemnosc >= pojemnosc_min)
    if wyposazenie_id:
        for w_id in wyposazenie_id:
            stmt = stmt.where(Salka.wyposazenie.any(Wyposazenie.id == w_id))
    stmt = stmt.order_by(Salka.nazwa)
    res = await session.execute(stmt)
    return list(res.scalars().unique().all())


@router.get("/{salka_id}", response_model=SalkaOdp)
async def szczegoly_salki(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(get_current_user),
) -> Salka:
    res = await session.execute(
        select(Salka).options(selectinload(Salka.wyposazenie)).where(Salka.id == salka_id)
    )
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Salka nie istnieje")
    return salka


@router.post("", response_model=SalkaOdp, status_code=status.HTTP_201_CREATED)
async def utworz_salke(
    dane: SalkaIn,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> Salka:
    wyposazenie = await _pobierz_wyposazenie(session, dane.wyposazenie_ids)
    salka = Salka(
        nazwa=dane.nazwa,
        pojemnosc=dane.pojemnosc,
        lokalizacja=dane.lokalizacja,
        aktywna=dane.aktywna,
        wyposazenie=wyposazenie,
    )
    session.add(salka)
    await session.commit()
    res = await session.execute(
        select(Salka).options(selectinload(Salka.wyposazenie)).where(Salka.id == salka.id)
    )
    return res.scalar_one()


@router.patch("/{salka_id}", response_model=SalkaOdp)
async def edytuj_salke(
    salka_id: int,
    dane: SalkaUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> Salka:
    res = await session.execute(
        select(Salka).options(selectinload(Salka.wyposazenie)).where(Salka.id == salka_id)
    )
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Salka nie istnieje")

    if dane.nazwa is not None:
        salka.nazwa = dane.nazwa
    if dane.pojemnosc is not None:
        salka.pojemnosc = dane.pojemnosc
    if dane.lokalizacja is not None:
        salka.lokalizacja = dane.lokalizacja
    if dane.aktywna is not None:
        salka.aktywna = dane.aktywna
    if dane.wyposazenie_ids is not None:
        salka.wyposazenie = await _pobierz_wyposazenie(session, dane.wyposazenie_ids)

    await session.commit()
    await session.refresh(salka)
    return salka


@router.delete("/{salka_id}", status_code=status.HTTP_204_NO_CONTENT)
async def usun_salke(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> None:
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Salka nie istnieje")
    await session.delete(salka)
    await session.commit()
