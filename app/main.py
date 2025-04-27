from fastapi import FastAPI
from database import engine
from models import Base
from auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecretkey"))

# Include router
app.include_router(auth_router)

# Create tables on startup file
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
