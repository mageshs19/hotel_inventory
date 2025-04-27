# crud.py

from models import Product
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ Get all products
async def get_all_products(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all()

# ✅ Create a new product
async def create_product(db: AsyncSession, name: str, description: str, price: float, quantity: int, branch: str):
    new_product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        branch=branch
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

# ✅ Delete a product by ID
async def delete_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product:
        await db.delete(product)
        await db.commit()
    return product

# ✅ Get a product by ID (for editing)
async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

# ✅ Update a product by ID
async def update_product(db: AsyncSession, product_id: int, name: str, description: str, price: float, quantity: int, branch: str):
    product = await get_product_by_id(db, product_id)
    if product:
        product.name = name
        product.description = description
        product.price = price
        product.quantity = quantity
        product.branch = branch
        await db.commit()
        await db.refresh(product)
    return product

# ✅ Get products only by branch
async def get_products_by_branch(db, branch: str):
    result = await db.execute(
        select(Product).where(Product.branch == branch)
    )
    return result.scalars().all()