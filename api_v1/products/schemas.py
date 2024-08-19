from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: str
    price: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductCreate):
    pass


class ProductUpdatePartial(ProductCreate):
    name: Optional[str] = None # type: ignore
    description: Optional[str] = None # type: ignore
    price: Optional[int] = None # type: ignore


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
