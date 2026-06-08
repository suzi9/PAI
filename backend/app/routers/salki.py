from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Salka, Wyposazenie
from app.schemas import SalkaIn, SalkaOdp, SalkaUpdate

router = APIRouter(prefix="/salki", tags=["salki"])

async def _pobierz_wyposazenie(session: AsyncSession, ids: list[int]):
    if ids is None:
        return []
    res = await session.execute(select(Wyposazenie).where(Wyposazenie.id.in_(ids)))
    return res.scalars().all()

@router.get("", response_model=list[SalkaOdp])
async def lista_salek(
    pojemnosc_min: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[Salka]:
    stmt = select(Salka)
    if pojemnosc_min:
        stmt = stmt.where(Salka.pojemnosc > pojemnosc_min)
    res = await session.execute(stmt)
    return res.scalars().all()

@router.get("/{salka_id}", response_model=SalkaOdp)
async def szczegoly_salki(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    res = await session.execute(
        select(Salka).options(selectinload(Salka.wyposazenie)).where(Salka.id == salka_id)
    )
    salka = res.scalar_one_or_none()
    if not salka:
        raise HTTPException(status_code=404, detail="Nie znaleziono")
    return salka

@router.post("", response_model=SalkaOdp, status_code=status.HTTP_201_CREATED)
async def utworz_salke(
    dane: SalkaIn,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    salka = Salka(
        nazwa=dane.nazwa,
        pojemnosc=dane.pojemnosc,
        lokalizacja=dane.lokalizacja,
        aktywna=dane.aktywna,
    )
    session.add(salka)
    await session.commit()
    await session.refresh(salka)
    return salka

@router.patch("/{salka_id}", response_model=SalkaOdp)
async def edytuj_salke(
    salka_id: int,
    dane: SalkaUpdate,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if not salka:
        raise HTTPException(status_code=404, detail="Nie znaleziono")
    if dane.aktywna:
        salka.aktywna = dane.aktywna
    await session.commit()
    return salka

@router.delete("/{salka_id}", status_code=status.HTTP_204_NO_CONTENT)
async def usun_salke(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if not salka:
        raise HTTPException(status_code=404, detail="Nie znaleziono")
    await session.delete(salka)
    await session.commit()