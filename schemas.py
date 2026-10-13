from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# User Registration Schema
class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User Response Schema
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


# JWT Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Product Creation Schema
class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    price: int = Field(gt=0)
    category: str = Field(min_length=2, max_length=100)
    stock: int = Field(ge=0)


# Product Response Schema
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    category: str
    stock: int

    class Config:
        from_attributes = True

# Cart Item Schema
class CartCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)