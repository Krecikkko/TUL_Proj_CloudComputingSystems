# Authentication Module

This document provides technical documentation for the **User
Authentication and Authorization** module.\
**Author:** Laura Gabryjańczyk

------------------------------------------------------------------------

## Setup & Configuration

### Environment

This module is part of a backend system built with **FastAPI** and
**SQLAlchemy**.\
To run it locally, you will need:

-   Python **3.10+**
-   `pip` and `virtualenv`

### Project Structure

The module is located under the backend application:

    backend/app/
    ├── main.py
    ├── db.py
    ├── models/
    │   └── user.py
    ├── routes/
    │   └── auth.py
    ├── schemas/
    │   ├── auth.py
    │   ├── user.py
    │   └── me.py
    └── utils/
        ├── security.py
        ├── auth_deps.py
        └── config.py

### Installation

To set up a virtual environment and install dependencies:

``` bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database

The module uses **SQLAlchemy** with asynchronous sessions.\
Default development configuration uses **SQLite**. The database is
created automatically on first run.

To create tables:

``` bash
alembic upgrade head
```

### Running the Server

From the `backend/` directory:

``` bash
uvicorn app.main:app --reload
```

Open the Swagger UI at:\
http://localhost:8000/docs

------------------------------------------------------------------------

## User Management

Users are registered and authenticated using JWT tokens.\
Each user has one of the following roles:

-   `user` --- standard access (default)
-   `admin` --- has access to protected routes

### User Data Storage

The `users` table schema is as follows:

  -------------------------------------------------------------------------
  Field               Type                  Description
  ------------------- --------------------- -------------------------------
  `id`                Integer (PK)          Unique user ID

  `username`          String                Unique username

  `email`             String                Unique email address

  `hashed_password`   String                Password hashed using `bcrypt`

  `role`              Enum(`admin`, `user`) Access level in the system

  `created_at`        DateTime              Account creation timestamp
  -------------------------------------------------------------------------

------------------------------------------------------------------------

## JWT Authentication

Authentication uses JSON Web Tokens (**JWT**) for secure sessions.

### Token Properties

  -----------------------------------------------------------------------
  Property              Value
  --------------------- -------------------------------------------------
  Algorithm             `HS256`

  Secret key            Defined in `app/utils/config.py` (secure in
                        production)

  Expiration            Managed by `access_token_expires()`

  Claims                `sub` (user ID), `username`, `iat`, `exp`
  -----------------------------------------------------------------------

Example decoded JWT payload:

``` json
{
  "sub": "1",
  "username": "user1",
  "iat": 1731164400,
  "exp": 1731168000
}
```

------------------------------------------------------------------------

## Role-Based Access Control (RBAC)

Role validation is implemented using dependency injection:

``` python
from app.utils.auth_deps import require_roles

@router.get("/admin/ping")
async def admin_ping(_: User = Depends(require_roles("admin"))):
    return {"ok": True}
```

If the user lacks permissions, the server returns:

``` json
{"detail": "Insufficient role"}
```

------------------------------------------------------------------------

## API Endpoints

### `POST /api/register`

Registers a new user.

-   Password is hashed using bcrypt.
-   Default role: `user`.
-   Checks for unique username and email.

**Example:**

``` bash
curl -X POST http://localhost:8000/api/register   -H "Content-Type: application/json"   -d '{"username":"user1","email":"user1@example.com","password":"SuperHaslo123"}'
```

**Response:**

``` json
{"message": "User created successfully"}
```

------------------------------------------------------------------------

### `POST /api/login`

Authenticates user credentials and returns a JWT token.

**Example:**

``` bash
curl -X POST http://localhost:8000/api/login   -H "Content-Type: application/json"   -d '{"username":"user1","password":"SuperHaslo123"}'
```

**Response:**

``` json
{
  "token": "JWT_TOKEN",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "role": "user"
  }
}
```

------------------------------------------------------------------------

### `GET /api/me`

Returns information about the currently authenticated user.

Requires header:

    Authorization: Bearer <JWT_TOKEN>

**Example:**

``` bash
curl http://localhost:8000/api/me   -H "Authorization: Bearer JWT_TOKEN"
```

**Response:**

``` json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "role": "user"
}
```

------------------------------------------------------------------------

### `POST /api/logout`

Performs logical logout (client-side only).\
No server-maintained token blacklist.

**Example:**

``` bash
curl -X POST http://localhost:8000/api/logout   -H "Authorization: Bearer JWT_TOKEN"
```

**Response:**\
HTTP `204 No Content`

------------------------------------------------------------------------

### `PUT /api/users/me`

Updates the current user's profile (username, email) and optionally
password.

**Authorization:**

    Authorization: Bearer <JWT_TOKEN>

**Body Schema (`UserUpdateIn`)** --- all fields are optional.

  ------------------------------------------------------------------------------
  Field            Type              Notes
  ---------------- ----------------- -------------------------------------------
  `username`       Optional\[str\]   New username

  `email`          Optional\[str\]   New email address

  `old_password`   Optional\[str\]   Required if `new_password` is provided

  `new_password`   Optional\[str\]   New password (minimum 8 characters)
  ------------------------------------------------------------------------------

**Example: Update Email**

``` bash
curl -X PUT http://localhost:8000/api/users/me   -H "Content-Type: application/json"   -H "Authorization: Bearer JWT_TOKEN"   -d '{"email": "user1_new@example.com"}'
```

**Example: Update Password**

``` bash
curl -X PUT http://localhost:8000/api/users/me   -H "Content-Type: application/json"   -H "Authorization: Bearer JWT_TOKEN"   -d '{"old_password": "SuperHaslo123", "new_password": "MegaSecure456"}'
```

**Response (Success):**

``` json
{
  "id": 1,
  "username": "user1",
  "email": "user1_new@example.com"
}
```

**Response (Error):**

``` json
{
  "detail": "Invalid old password"
}
```

------------------------------------------------------------------------

## Summary

  Component          Description
  ------------------ ---------------------------------------------------
  Framework          FastAPI
  ORM                SQLAlchemy (Async)
  Authentication     JWT (HTTP Bearer)
  Password Hashing   bcrypt
  Security           Rate Limiting (Redis) on `/login` and `/register`
  Endpoint Added     `PUT /api/users/me`
  User Roles         `user`, `admin`
  API Docs           Available at `/docs` (Swagger UI)
  Database           SQLite (dev), compatible with PostgreSQL/MySQL
