from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, rezerwacje, salki, wyposazenie

app = FastAPI(
    title="System rezerwacji salek",
    version="1.0.0",
    description="API do zarzadzania salkami konferencyjnymi i ich rezerwacjami.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(salki.router)
app.include_router(wyposazenie.router)
app.include_router(rezerwacje.router)