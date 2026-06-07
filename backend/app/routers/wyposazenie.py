from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user, wymagaj_admina
from app.models import Wyposazenie
from app.schemas import WyposazenieIn, WyposazenieOdp

router = APIRouter(prefix="/wyposazenie", tags=["wyposazenie"])


@router.get("", response_model=list[WyposazenieOdp])
async def lista_wyposazenia(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(get_current_user),
) -> list[Wyposazenie]:
    res = await session.execute(select(Wyposazenie).order_by(Wyposazenie.nazwa))
    return list(res.scalars().all())


@router.post("", response_model=WyposazenieOdp, status_code=status.HTTP_201_CREATED)
async def utworz_wyposazenie(
    dane: WyposazenieIn,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> Wyposazenie:
    w = Wyposazenie(nazwa=dane.nazwa)
    session.add(w)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wyposazenie o takiej nazwie juz istnieje",
        )
    await session.refresh(w)
    return w


@router.delete("/{wyposazenie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def usun_wyposazenie(
    wyposazenie_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(wymagaj_admina),
) -> None:
    res = await session.execute(select(Wyposazenie).where(Wyposazenie.id == wyposazenie_id))
    w = res.scalar_one_or_none()
    if w is None:
        raise HTTPException(status_code=404, detail="Wyposazenie nie istnieje")
    await session.delete(w)
    await session.commit()
