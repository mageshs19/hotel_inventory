# app/admin_router.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
from crud import get_all_products, create_product, delete_product, get_product_by_id, update_product

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# ✅ Admin dashboard: View all products
@router.get("/admin/dashboard")
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return RedirectResponse("/login")  # force back to login if not admin

    products = await get_all_products(db)
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "products": products
    })

# ✅ Admin - Add new product
@router.post("/admin/add-product")
async def add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
    branch: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    await create_product(db, name, description, price, quantity, branch)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

# ✅ Admin - Delete product
@router.get("/admin/delete-product/{product_id}")
async def delete_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    await delete_product(db, product_id)
    return RedirectResponse(url="/admin/dashboard", status_code=302)

# ✅ Admin - Edit product (Form)
@router.get("/admin/edit-product/{product_id}")
async def edit_product_form(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    product = await get_product_by_id(db, product_id)
    if product:
        return templates.TemplateResponse("edit_product.html", {
            "request": request,
            "product": product
        })
    return RedirectResponse(url="/admin/dashboard")

# ✅ Admin - Update product (After editing)
@router.post("/admin/update-product/{product_id}")
async def update_product_details(
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
    branch: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    await update_product(db, product_id, name, description, price, quantity, branch)
    return RedirectResponse(url="/admin/dashboard", status_code=302)
