from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to StyleHub API"
    }


def test_list_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_details():
    response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Cotton T-Shirt"


def test_register_user():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/register/",
        json={
            "name": "Test User",
            "email": unique_email,
            "password": "TestPass123"
        }
    )

    assert response.status_code in [200, 201]


def test_login_user():
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    # First, register a new user
    register_response = client.post(
        "/register/",
        json={
            "name": "Login Test User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code in [200, 201]

    # Then, log in with the same credentials
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"

def test_get_current_user():
    email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    register_response = client.post(
        "/register/",
        json={
            "name": "Me Test User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == email

def test_login_invalid_password():
    email = f"invalid_{uuid.uuid4().hex[:8]}@example.com"

    register_response = client.post(
        "/register/",
        json={
            "name": "Invalid Login Test",
            "email": email,
            "password": "CorrectPass123"
        }
    )

    assert register_response.status_code in [200, 201]

    response = client.post(
        "/login",
        json={
            "email": email,
            "password": "WrongPass123"
        }
    )

    assert response.status_code == 401



def test_me_without_token():
    response = client.get("/me")

    assert response.status_code == 401

def test_me_with_invalid_token():
    response = client.get(
        "/me",
        headers={
            "Authorization": "Bearer invalid_token_123"
        }
    )

    assert response.status_code == 401

def test_add_to_cart():
    email = f"cart_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    # Register user
    register_response = client.post(
        "/register/",
        json={
            "name": "Cart Test User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    # Login user
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Add product to cart
    cart_response = client.post(
        "/cart",
        json={
            "product_id": 1,
            "quantity": 1
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert cart_response.status_code == 201

def test_add_to_cart_without_token():
    response = client.post(
        "/cart",
        json={
            "product_id": 1,
            "quantity": 1
        }
    )

    assert response.status_code == 401

def test_view_cart():
    email = f"viewcart_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    client.post(
        "/register/",
        json={
            "name": "View Cart User",
            "email": email,
            "password": password
        }
    )

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add product to cart
    add_response = client.post(
        "/cart",
        json={"product_id": 1, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert add_response.status_code == 201

    # View cart
    cart_response = client.get(
        "/cart",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert cart_response.status_code == 200

def test_place_order():
    email = f"order_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    # Register user
    register_response = client.post(
        "/register/",
        json={
            "name": "Order Test User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    # Login user
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add product to cart
    cart_response = client.post(
        "/cart",
        json={"product_id": 1, "quantity": 1},
        headers=headers
    )
    assert cart_response.status_code == 201

    # Place order
    order_response = client.post(
        "/orders",
        headers=headers
    )

    assert order_response.status_code == 201
    assert order_response.json()["total_amount"] == 799

def test_place_order_with_empty_cart():
    email = f"emptyorder_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    register_response = client.post(
        "/register/",
        json={
            "name": "Empty Cart User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/orders",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Your cart is empty"

def test_payment_success():
    email = f"payment_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    # Register user
    register_response = client.post(
        "/register/",
        json={
            "name": "Payment Test User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    # Login user
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add product to cart
    cart_response = client.post(
        "/cart",
        json={"product_id": 1, "quantity": 1},
        headers=headers
    )
    assert cart_response.status_code == 201

    # Place order
    order_response = client.post(
        "/orders",
        headers=headers
    )
    assert order_response.status_code == 201

    order_id = order_response.json()["order_id"]

    # Make mock payment
    payment_response = client.post(
        f"/payments/{order_id}?payment_result=success",
        headers=headers
    )

    assert payment_response.status_code == 200
    assert payment_response.json()["payment_status"] == "SUCCESS"


def test_payment_failure():
    email = f"payment_fail_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    # Register user
    register_response = client.post(
        "/register/",
        json={
            "name": "Payment Failure User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    # Login user
    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add product to cart
    cart_response = client.post(
        "/cart",
        json={
            "product_id": 1,
            "quantity": 1
        },
        headers=headers
    )
    assert cart_response.status_code == 201

    # Place order
    order_response = client.post(
        "/orders",
        headers=headers
    )
    assert order_response.status_code == 201

    order_id = order_response.json()["order_id"]

    # Simulate payment failure
    payment_response = client.post(
        f"/payments/{order_id}?payment_result=failure",
        headers=headers
    )

    assert payment_response.status_code == 200
    assert payment_response.json()["payment_status"] == "FAILED"

def test_get_payment_history():
    email = f"payment_history_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    register_response = client.post(
        "/register/",
        json={
            "name": "Payment History User",
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code in [200, 201]

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/payments", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_payment_without_token():
    response = client.post(
        "/payments/1?payment_result=success"
    )

    assert response.status_code == 401

def test_payment_again_after_success():
    email = f"payment_again_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123"

    client.post(
        "/register/",
        json={
            "name": "Payment Retry User",
            "email": email,
            "password": password
        }
    )

    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cart_response = client.post(
        "/cart",
        json={"product_id": 1, "quantity": 1},
        headers=headers
    )
    assert cart_response.status_code == 201

    order_response = client.post(
        "/orders",
        headers=headers
    )
    assert order_response.status_code == 201

    order_id = order_response.json()["order_id"]

    first_payment = client.post(
        f"/payments/{order_id}?payment_result=success",
        headers=headers
    )
    assert first_payment.status_code == 200

    second_payment = client.post(
        f"/payments/{order_id}?payment_result=success",
        headers=headers
    )

    assert second_payment.status_code == 400
    assert second_payment.json()["detail"] == (
        "Payment already successful for this order"
    )