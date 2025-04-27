from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
from sqlalchemy.future import select
from models import Product  
from crud import get_products_by_branch, create_product, update_product, delete_product, get_product_by_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# ✅ Manager Dashboard
@router.get("/manager/dashboard")
async def manager_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")

    # 1️⃣ check if user is logged in and is manager
    if not user or user["role"] != "manager":
        return RedirectResponse(url="/login")

    # 2️⃣ fetch own branch products
    result = await db.execute(select(Product).where(Product.branch == user['branch']))
    my_products = result.scalars().all()

    # 3️⃣ fetch other branch products (all except my branch)
    result = await db.execute(select(Product).where(Product.branch != user['branch']))
    other_products = result.scalars().all()

    # 4️⃣ render page
    return templates.TemplateResponse("manager_dashboard.html", {
        "request": request,
        "products": my_products,
        "other_products": other_products,
        "user": user
    })


# ✅ Manager - Add Product (Post)
@router.post("/manager/add-product")
async def manager_add_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    branch = user.get("branch")
    await create_product(db, name, description, price, quantity, branch)
    return RedirectResponse(url="/manager/dashboard", status_code=302)

# ✅ Manager - Edit Product Form (Page)
@router.get("/manager/edit-product/{product_id}")
async def manager_edit_product_form(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    product = await get_product_by_id(db, product_id)

    # ✅ Check if the manager is editing only their branch product
    if product and product.branch == user['branch']:
        return templates.TemplateResponse("manager_edit_product.html", {
            "request": request,
            "product": product,
            "user": user
        })
    else:
        return RedirectResponse(url="/manager/dashboard", status_code=302)

# ✅ Manager - Update Product (Post)
@router.post("/manager/update-product/{product_id}")
async def manager_update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    product = await get_product_by_id(db, product_id)

    # ✅ Allow update only if the branch matches
    if product and product.branch == user['branch']:
        await update_product(db, product_id, name, description, price, quantity, branch=user['branch'])

    return RedirectResponse(url="/manager/dashboard", status_code=302)

# ✅ Manager - Delete Product (Optional, if needed)
@router.get("/manager/delete-product/{product_id}")
async def manager_delete_product(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=302)

    product = await get_product_by_id(db, product_id)

    # ✅ Allow delete only if the branch matches
    if product and product.branch == user['branch']:
        await delete_product(db, product_id)

    return RedirectResponse(url="/manager/dashboard", status_code=302)
