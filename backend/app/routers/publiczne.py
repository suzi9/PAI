from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Rezerwacja, Salka

router = APIRouter(prefix="/publiczne", tags=["publiczne"])


@router.get("/salki")
async def publiczne_salki(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Salka)
        .options(selectinload(Salka.wyposazenie))
        .where(Salka.aktywna.is_(True))
        .order_by(Salka.nazwa)
    )
    res = await session.execute(stmt)
    return [
        {
            "id": s.id,
            "nazwa": s.nazwa,
            "lokalizacja": s.lokalizacja,
            "pojemnosc": s.pojemnosc,
            "wyposazenie": [
                {"id": w.id, "nazwa": w.nazwa} for w in s.wyposazenie
            ],
        }
        for s in res.scalars().all()
    ]


@router.get("/dostepnosc")
async def publiczna_dostepnosc(session: AsyncSession = Depends(get_session)):
    teraz = datetime.now(tz=timezone.utc)
    stmt = (
        select(Rezerwacja)
        .options(selectinload(Rezerwacja.salka))
        .where(Rezerwacja.status == "aktywna")
        .where(Rezerwacja.do_ >= teraz)
        .order_by(Rezerwacja.od)
    )
    res = await session.execute(stmt)
    rezerwacje = res.scalars().all()
    return [
        {
            "salka_id": r.salka_id,
            "salka": r.salka.nazwa,
            "lokalizacja": r.salka.lokalizacja,
            "tytul": r.tytul,
            "od": r.od.isoformat(),
            "do": r.do_.isoformat(),
        }
        for r in rezerwacje
    ]
