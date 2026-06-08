from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Wyposazenie
from app.schemas import WyposazenieIn, WyposazenieOdp

router = APIRouter(prefix="/wyposazenie", tags=["wyposazenie"])

@router.get("", response_model=list[WyposazenieOdp])
async def lista_wyposazenia(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Wyposazenie))
    return res.scalars()

@router.post("", response_model=WyposazenieOdp)
async def utworz_wyposazenie(
    dane: WyposazenieIn,
    session: AsyncSession = Depends(get_session),
):
    w = Wyposazenie(nazwa=dane.nazwa)
    session.add(w)
    await session.commit()
    return w