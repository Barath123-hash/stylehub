from typing import List

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models import User, Product, Cart, Order, OrderItem, Payment
from schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    ProductCreate,
    ProductResponse,
    CartCreate
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

app = FastAPI(title="StyleHub Fashion Mini Store API")

Base.metadata.create_all(bind=engine)

bearer_scheme = HTTPBearer()


@app.get("/")
def home():
    return {"message": "Welcome to StyleHub API"}


@app.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    return new_user


@app.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_error

    return user


@app.get("/products", response_model=List[ProductResponse])
def get_products(
    sort: str = "default",
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())

    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    elif sort != "default":
        raise HTTPException(
            status_code=400,
            detail="Invalid sort option. Use price_asc or price_desc"
        )

    return query.all()

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@app.get("/products/filter", response_model=List[ProductResponse])
def filter_products(
    category: str = None,
    min_price: int = None,
    max_price: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category.ilike(category))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.all()

@app.post("/cart", status_code=201)
def add_to_cart(
    cart_data: CartCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    product = db.query(Product).filter(
        Product.id == cart_data.product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart_item = Cart(
        user_id=user_id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart successfully",
        "cart_id": cart_item.id,
        "user_id": cart_item.user_id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }

@app.get("/cart")
def get_cart(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    cart_items = db.query(Cart).filter(
        Cart.user_id == user_id
    ).all()

    result = []

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            result.append({
                "cart_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": product.price * item.quantity
            })

    return {
        "user_id": user_id,
        "items": result,
        "total_items": sum(item["quantity"] for item in result),
        "total_price": sum(item["subtotal"] for item in result)
    }

@app.delete("/cart/{cart_id}")
def remove_from_cart(
    cart_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    cart_item = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == user_id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}

@app.post("/orders", status_code=201)
def place_order(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    cart_items = db.query(Cart).filter(
        Cart.user_id == user_id
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Your cart is empty"
        )

    total_amount = 0

    for item in cart_items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        if item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock for " + product.name
            )

        total_amount += product.price * item.quantity

    try:
        new_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="PLACED"
        )
        db.add(new_order)
        db.flush()

        for item in cart_items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(order_item)

            product.stock -= item.quantity
            db.delete(item)

        db.commit()
        db.refresh(new_order)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not place order"
        )

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }

@app.get("/orders")
def get_orders(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.id.desc()).all()

    result = []

    for order in orders:
        items = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()

        order_items = []

        for item in items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            order_items.append({
                "product_id": item.product_id,
                "product_name": product.name if product else "Product unavailable",
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.quantity * item.price
            })

        result.append({
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": order_items
        })

    return result

@app.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
    User.id == user_id
).first()

    if user is None or user.role != "admin":
        raise HTTPException(
        status_code=403,
        detail="Admin access required"
    )

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_statuses = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED"]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    order.status = new_status
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }

import uuid

@app.post("/payments/{order_id}")
def create_mock_payment(
    order_id: int,
    payment_result: str = "success",
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    successful_payment = db.query(Payment).filter(
    Payment.order_id == order_id,
    Payment.status == "SUCCESS"
).first()

    if successful_payment:
        raise HTTPException(
        status_code=400,
        detail="Payment already successful for this order"
    )
    
    if order.status != "PLACED":
        raise HTTPException(
        status_code=400,
        detail="Payment is only allowed for orders with PLACED status"
    )

    if payment_result not in ["success", "failure"]:
        raise HTTPException(
            status_code=400,
            detail="payment_result must be success or failure"
        )

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        status="SUCCESS" if payment_result == "success" else "FAILED",
        transaction_id=f"MOCK-{uuid.uuid4().hex[:12].upper()}"
    )

    db.add(payment)

    if payment_result == "success":
        order.status = "CONFIRMED"

    db.commit()
    db.refresh(payment)

    return {
        "message": "Mock payment processed",
        "order_id": order.id,
        "amount": payment.amount,
        "payment_status": payment.status,
        "order_status": order.status,
        "transaction_id": payment.transaction_id
    }

@app.get("/payments")
def get_payment_history(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    payments = (
        db.query(Payment)
        .join(Order, Payment.order_id == Order.id)
        .filter(Order.user_id == user_id)
        .order_by(Payment.id.desc())
        .all()
    )

    return [
        {
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "payment_status": payment.status,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at
        }
        for payment in payments
    ]