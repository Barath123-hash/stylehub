StyleHub – Fashion Mini Store
Project Overview

StyleHub is a backend-only fashion mini store application built using FastAPI and SQLite. It provides user authentication, product management, shopping cart, order processing, and mock payment functionality.

Technologies Used
Python
FastAPI
SQLite
SQLAlchemy
JWT Authentication
Pytest
Swagger UI
Features
User registration and login
JWT-based authentication
Get current logged-in user
Create and view products
Filter products by category and price
Sort products by price
Add products to cart
View and remove cart items
Place orders and track order status
Automatic stock reduction after order placement
Mock payment success and failure
Payment history
Prevent duplicate successful payments
Automated API testing with Pytest
Project Structure
stylehub/
├── auth.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── test_main.py
├── stylehub.db
├── README.md
└── venv/
Installation and Setup
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_URL
cd stylehub
2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install fastapi uvicorn sqlalchemy pyjwt "passlib[bcrypt]" pytest httpx
4. Start the application
uvicorn main:app --reload
5. Open API documentation

Visit:

http://127.0.0.1:8000/docs

Automated Testing

Run all tests:

pytest -v test_main.py

The project currently has 19 passing automated tests.

Payment Information

This project uses simulated payments for testing. It does not process real payments through Stripe or another payment gateway.

Security
Passwords are hashed.
Protected endpoints require JWT authentication.
Users can access their own protected resources.
Duplicate successful payments are prevented.
Future Improvements
Integrate a real payment gateway in test mode.
Add isolated test database configuration.
Improve validation and error handling.
Add more automated tests and API documentation.
Author

StyleHub Backend Project