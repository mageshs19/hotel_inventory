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
        # ✅ Save session
        request.session['user'] = {
            "username": user.username,
            "role": user.role,
            "branch": user.branch
        }

        # ✅ Redirect based on role
        if user.role == "admin":
            return RedirectResponse("/admin/dashboard", status_code=302)
        elif user.role == "manager":
            return RedirectResponse("/manager/dashboard", status_code=302)
        else:
            # Future proofing (if other roles added)
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Unknown role"
            })

    else:
        # Login failed
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })


# ✅ GET - Logout
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
