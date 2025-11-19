# Authentication Module

This document provides technical documentation for the **User Authentication and Authorization** module.  
**Author:** Laura Gabryjańczyk

---

## Setup & Configuration

### Environment

This module is part of a backend system built with **FastAPI** and **SQLAlchemy**.  
To run it locally, you will need:

- Python **3.10+**
- `pip` and `virtualenv`

### Project Structure

The module is located under the backend application:

```
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
```

### Installation

To set up a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database

The module uses **SQLAlchemy** with asynchronous sessions.  
The default development configuration uses **SQLite**. The database is created automatically on first run.

To create tables:

```bash
alembic upgrade head
```

### Running the Server

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

Open the Swagger UI at:  
http://localhost:8000/docs

---


## User Management

Users are registered and authenticated using JWT tokens.  
Each user has one of the following roles:

- `user` — standard access (default)
- `admin` — elevated access for protected routes

### User Data Storage

The `users` table schema is as follows:

| Field             | Type                  | Description |
|-------------------|-----------------------|-------------|
| `id`              | Integer (PK)          | Unique user ID |
| `username`        | String                | Unique username |
| `email`           | String                | Unique email address |
| `hashed_password` | String                | Password hashed using `bcrypt` |
| `role`            | Enum(`admin`, `user`) | Access level |
| `created_at`      | DateTime              | Account creation timestamp |

---

## JWT Authentication

Authentication uses **JSON Web Tokens (JWT)** for secure sessions.

### Token Properties

| Property     | Value |
|--------------|--------|
| Algorithm    | `HS256` |
| Secret key   | Defined in `app/utils/config.py` |
| Expiration   | Managed by `access_token_expires()` |
| Claims       | `sub`, `username`, `iat`, `exp` |

Example decoded payload:

```json
{
  "sub": "1",
  "username": "user1",
  "iat": 1731164400,
  "exp": 1731168000
}
```

---

## Role-Based Access Control (RBAC)

Access validation uses dependency injection:

```python
from app.utils.auth_deps import require_roles

@router.get("/admin/ping")
async def admin_ping(_: User = Depends(require_roles("admin"))):
    return {"ok": True}
```

Unauthorized access returns:

```json
{"detail": "Insufficient role"}
```

---

## API Endpoints

### `POST /api/register`
Registers a new user.

### `POST /api/login`
Authenticates a user and returns a JWT.

### `GET /api/me`
Returns authenticated user data.

### `POST /api/logout`
Performs a client-side logout.

### `PUT /api/users/me`
Updates the user's own profile or password.

---

## 2. New User Management Endpoints

### **User Endpoints (require authorization)**

#### `GET /api/users/stats`
Returns file statistics for the currently authenticated user.

**Example response:**
```json
{"files_uploaded": 12, "storage_used": "1.45 GB"}
```

---

### **Administrative Endpoints**
All require **admin role** and the dependency:
```
require_roles("admin")
```

#### `GET /api/admin/users`
Returns a list of all user accounts.

#### `DELETE /api/admin/users/{user_id}`
Permanently deletes a user account and all associated files.

#### `PUT /api/admin/users/{user_id}/role`
Updates a user's role.

**Body:**
```json
{"role": "admin"}
```

---

## 3. Updated Data Schemas

### **UserOut Schema (updated)**

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | User ID |
| `username` | str | Username |
| `email` | EmailStr | Email address |
| `role` | str | User role (`user` or `admin`) |

---

## Summary

| Component        | Description |
|------------------|-------------|
| Framework        | FastAPI |
| ORM              | SQLAlchemy (Async) |
| Authentication   | JWT |
| New Endpoints    | User stats, admin user management |
| User Roles       | `user`, `admin` |
| API Docs         | `/docs` |
| Database         | SQLite (dev), compatible with PostgreSQL/MySQL |

