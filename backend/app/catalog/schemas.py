from datetime import datetime

from pydantic import BaseModel, Field


# --------------- Category ---------------

class CategoryCreate(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=120)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    slug: str | None = Field(default=None, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --------------- Product Image ---------------

class ProductImageCreate(BaseModel):
    url: str = Field(max_length=500)
    is_primary: bool = False
    sort_order: int = 0


class ProductImageResponse(BaseModel):
    id: str
    url: str
    is_primary: bool
    sort_order: int

    model_config = {"from_attributes": True}


# --------------- Product ---------------

class ProductCreate(BaseModel):
    name: str = Field(max_length=200)
    slug: str = Field(max_length=220)
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    category_id: str
    images: list[ProductImageCreate] = []


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=220)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    price: float
    stock: int
    category_id: str
    category: CategoryResponse
    images: list[ProductImageResponse]
    is_active: bool
    average_rating: float | None = None
    reviews_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    id: str
    name: str
    slug: str
    price: float
    stock: int
    category: CategoryResponse
    primary_image: str | None
    is_active: bool
    average_rating: float | None = None
    reviews_count: int = 0

    model_config = {"from_attributes": True}


# --------------- Pagination ---------------

class PaginatedProducts(BaseModel):
    items: list[ProductListResponse]
    total: int
    page: int
    per_page: int
    pages: int
