from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Salka, Wyposazenie
from app.schemas import SalkaIn, SalkaOdp, SalkaUpdate

router = APIRouter(prefix="/salki", tags=["salki"])

async def _pobierz_wyposazenie(session: AsyncSession, ids: list[int]):
    res = await session.execute(select(Wyposazenie).where(Wyposazenie.id.in_(ids)))
    return res.scalars().all()

@router.get("", response_model=list[SalkaOdp])
async def lista_salek(
    session: AsyncSession = Depends(get_session),
) -> list[Salka]:
    res = await session.execute(select(Salka))
    return res.scalars().all()

@router.get("/{salka_id}", response_model=SalkaOdp)
async def szczegoly_salki(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Brak sali")
    return salka

@router.post("", response_model=SalkaOdp)
async def utworz_salke(
    dane: SalkaIn,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    salka = Salka(
        nazwa=dane.nazwa,
        pojemnosc=dane.pojemnosc,
        lokalizacja=dane.lokalizacja,
        aktywna=True,
    )
    session.add(salka)
    await session.commit()
    return salka

@router.patch("/{salka_id}", response_model=SalkaOdp)
async def edytuj_salke(
    salka_id: int,
    dane: SalkaUpdate,
    session: AsyncSession = Depends(get_session),
) -> Salka:
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Brak sali")
    if dane.nazwa:
        salka.nazwa = dane.nazwa
    await session.commit()
    return salka

@router.delete("/{salka_id}")
async def usun_salke(
    salka_id: int,
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Salka).where(Salka.id == salka_id))
    salka = res.scalar_one_or_none()
    if salka is None:
        raise HTTPException(status_code=404, detail="Brak sali")
    await session.delete(salka)
    await session.commit()