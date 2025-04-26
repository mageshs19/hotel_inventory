from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import SessionLocal
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Correctly define get_db function
async def get_db():
    async with SessionLocal() as session:
        yield session

# ✅ GET - Login page
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ POST - Handle login
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.username == username, User.password == password)
    )
    user = result.scalars().first()

    if user:
        # ✅ Save user info into session
        request.session['user'] = {"username": user.username}
        return RedirectResponse("/welcome", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# ✅ GET - Welcome page (After login)
@router.get("/welcome")
async def welcome_page(request: Request):
    user = request.session.get("user")
    if user:
        return templates.TemplateResponse("welcome.html", {"request": request, "username": user["username"]})
    else:
        return RedirectResponse("/login")

# ✅ GET - Logout
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
