from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import squads

from database import Base, engine

from routes import auth
from routes import pages
from routes import squads
from routes import habits
from routes import leaderboard

from routes import at_risk


# Create Database Tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Squad Habits",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# Routers
app.include_router(pages.router)
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    at_risk.router,
    prefix="/at_risk",
    tags=["RiskMembers"]
)


app.include_router(
    habits.router,
    prefix="/api/habits",
    tags=["Habits"]
)
app.include_router(
    leaderboard.router,
    prefix="/api/leaderboard",
    tags=["Leaderboard"]
)
app.include_router(
    squads.router,
    prefix="/api/squads",
    tags=["Squads"]
)

app.include_router(
    squads.router,
    prefix="/api/squads",
    tags=["Squads"]
)


@app.get("/health")
async def health():
    return {
        "status": "OK",
        "message": "Squad Habits API Running"
    }