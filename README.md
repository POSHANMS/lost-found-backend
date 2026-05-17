# FindIt — Campus Lost & Found Portal (Backend)

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-Upstash-DC382D?style=for-the-badge&logo=redis)](https://upstash.com)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Storage-3448C5?style=for-the-badge&logo=cloudinary)](https://cloudinary.com)
[![Socket.io](https://img.shields.io/badge/Flask--SocketIO-5.3-010101?style=for-the-badge&logo=socketdotio)](https://flask-socketio.readthedocs.io)

> REST API backend for the FindIt campus lost & found platform. Built with Flask, PostgreSQL on Supabase, Redis caching on Upstash, Socket.io real-time events, JWT authentication, Marshmallow validation, and rate limiting.

---

## 🔗 Links

> **Live API:** [https://findit-backend.onrender.com](https://findit-backend.onrender.com)
> **Frontend Repo:** [https://github.com/POSHANMS/lost-found-frontend](https://github.com/POSHANMS/lost-found-frontend)

---

## ✨ Features

### Authentication & Users
- [x] Register with name, email, phone, department, password
- [x] Password hashing with bcrypt (12 salt rounds)
- [x] JWT access token (expires in 30 minutes)
- [x] Login with email + password validation
- [x] Basic refresh token implemented
- [x] `/me` endpoint to restore session on page refresh
- [x] Logout endpoint
- [x] Role-based access control (student / admin)
- [x] User ban / unban system (banned users cannot login)
- [x] `token_required` decorator for protected routes
- [x] `admin_required` decorator for admin-only routes

### Items
- [x] Create lost or found item with title, description, category, status, location
- [x] Accept image URL from Cloudinary (frontend uploads directly, backend stores URL only)
- [x] Store `image_public_id` for future deletion
- [x] Store `latitude` and `longitude` for map pin
- [x] Store `verification_question` and `verification_answer` (anti-fraud)
- [x] Edit item (owner only)
- [x] Delete item (owner only) — clears Redis cache immediately
- [x] Mark item as resolved via `is_resolved` flag
- [x] Filter items by status (lost/found), category, search term
- [x] Filter by current user (`?my=true` — reads token without requiring `@token_required`)
- [x] Case-insensitive title search with `ilike`
- [x] Paginated results with `page` and `per_page` params
- [x] Redis caching on all list endpoints (5 minute expiry)
- [x] Cache auto-invalidated on create, update, delete

### Claims
- [x] Submit claim with answer to verification question
- [x] Flexible partial answer matching (case-insensitive)
- [x] Wrong answer rejected with 400 before claim is created
- [x] Duplicate claim prevention (one claim per user per item)
- [x] Owner cannot claim their own item
- [x] Owner can view all claims on their item
- [x] Owner can approve or reject claims
- [x] Approved claim marks item as `is_resolved = True`
- [x] My claims endpoint (`/claims/mine`) for dashboard

### Notifications
- [x] Notification created when someone claims an item (to owner)
- [x] Notification created when claim is approved or rejected (to claimant)
- [x] Get all notifications for current user
- [x] Mark specific notification as read
- [x] Mark all notifications as read

### Real-time (Socket.io)
- [x] Users join personal room on login: `user_{id}`
- [x] Emit notification to owner's room on claim submission
- [x] Emit notification to claimant's room on claim approval/rejection
- [x] CORS configured for frontend origin

### Email Notifications
- [x] Email to item owner when someone claims their item
- [x] Email to claimant when claim is approved or rejected
- [x] Email failures don't break the API (wrapped in try/except)
- [x] Gmail SMTP via Flask-Mail

### Caching (Redis on Upstash)
- [x] Browse items cached by page + filters + search
- [x] Admin stats cached for 10 minutes
- [x] `cache_delete_pattern("items:*")` clears all item caches on any change
- [x] `json.loads()` used correctly (not `json.load()`)

### Validation (Marshmallow)
- [x] Register: name (2-50 chars), email (valid format), password (8+ chars), phone (10-15 chars), department (required)
- [x] Login: email + password required
- [x] Item: title, description, category, status, location required; category from allowed list
- [x] Claim: answer required, optional message

### Rate Limiting (Flask-Limiter)
- [x] Login: 10 per minute (brute force protection)
- [x] Register: 5 per minute (spam prevention)
- [x] Rate limit storage backed by Redis

### Admin
- [x] View all users with ban status and role
- [x] Ban or unban any non-admin user (toggle)
- [x] View all items across all users
- [x] Delete any item (admin moderation) — clears cache
- [x] Platform statistics (users, items, lost, found, resolved, claims)

---

## 🛠️ Tech Stack

| Category | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.13 | Core language |
| Framework | Flask | 3.0 | REST API |
| Database | PostgreSQL | 16 | Primary data store |
| DB Host | Supabase | Free tier | Managed PostgreSQL (free forever) |
| ORM | Flask-SQLAlchemy | 3.1 | Database models + queries |
| Validation | Flask-Marshmallow | 1.2 | Input schema validation |
| Auth | PyJWT | 2.8 | JWT encode/decode |
| Passwords | bcrypt | 4.1 | Password hashing |
| Real-time | Flask-SocketIO | 5.3 | WebSocket events |
| Caching | redis-py | 5.0 | Redis client |
| Cache Host | Upstash | Free tier | Managed Redis (free forever) |
| Rate Limiting | Flask-Limiter | 3.5 | Request rate limiting |
| Email | Flask-Mail | 0.10 | Gmail SMTP |
| Image Storage | Cloudinary | — | CDN + image storage |
| CORS | Flask-CORS | 4.0 | Cross-origin requests |
| Testing | pytest + pytest-flask | latest | Unit + integration tests |
| Container | Docker + docker-compose | latest | Local dev environment |

---

## 📁 Project Structure

```
lost-found-backend/
├── models/
│   ├── user.py            # User model — id, name, email, password, phone, department, role, is_banned
│   ├── item.py            # Item model — title, desc, category, status, location, lat, lng, image, verification
│   ├── claim.py           # Claim model — item_id, user_id, message, status (pending/approved/rejected)
│   └── notification.py    # Notification model — user_id, message, is_read
├── routes/
│   ├── auth.py            # register, login, /me, logout + token helpers
│   ├── items.py           # GET list, GET one, POST, PUT, DELETE + ?my=true filter
│   ├── claims.py          # POST claim, GET claims, PUT respond, GET /mine
│   ├── notifications.py   # GET all, PUT mark read
│   └── admin.py           # GET users, PUT ban, GET items, DELETE item, GET stats
├── schemas/
│   ├── user_schema.py     # RegisterSchema, LoginSchema
│   ├── item_schema.py     # ItemSchema (create/update)
│   └── claim_schema.py    # ClaimSchema, ClaimResponseSchema
├── utils/
│   ├── auth_middleware.py # @token_required, @admin_required decorators
│   ├── cache.py           # cache_get, cache_set, cache_delete, cache_delete_pattern
│   ├── cloudinary.py      # upload_image helper (for server-side uploads if needed)
│   └── email.py           # send_claim_notification, send_claim_response
├── tests/
│   ├── test_auth.py       # register, login, /me, token tests
│   ├── test_items.py      # CRUD, search, filter, pagination tests
│   └── test_claims.py     # claim submission, verification, approval tests
├── app.py                 # Flask app factory, blueprint registration, socket handlers
├── extensions.py          # db, ma, mail, socketio, limiter — initialized once, used everywhere
├── requirements.txt       # all Python dependencies pinned
├── Dockerfile             # container definition for Flask
├── docker-compose.yml     # starts Flask + PostgreSQL + Redis together
└── .env                   # secret keys and connection strings (never commit)
```

---

## 🗄️ Database Schema

### Users
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100)  NOT NULL
email           VARCHAR(150)  UNIQUE NOT NULL
password        VARCHAR(255)  NOT NULL       -- bcrypt hash, never plain text
phone           VARCHAR(20)   NOT NULL
department      VARCHAR(100)  NOT NULL
role            VARCHAR(20)   DEFAULT 'student'  -- 'student' or 'admin'
is_banned       BOOLEAN       DEFAULT FALSE
created_at      TIMESTAMP     DEFAULT NOW()
```

### Items
```sql
id                    SERIAL PRIMARY KEY
user_id               INTEGER  REFERENCES users(id)  NOT NULL
title                 VARCHAR(150)  NOT NULL
description           TEXT          NOT NULL
category              VARCHAR(50)   NOT NULL   -- Electronics, Documents, Accessories, Clothing, Keys, Bags, Other
status                VARCHAR(10)   NOT NULL   -- 'lost' or 'found'
location              VARCHAR(200)  NOT NULL   -- human readable location name
latitude              FLOAT         NULLABLE   -- map pin coordinates
longitude             FLOAT         NULLABLE   -- map pin coordinates
image_url             VARCHAR(500)  NULLABLE   -- Cloudinary CDN URL
image_public_id       VARCHAR(300)  NULLABLE   -- for future deletion from Cloudinary
verification_question VARCHAR(300)  NULLABLE   -- anti-fraud question
verification_answer   VARCHAR(300)  NULLABLE   -- never returned in API responses
is_resolved           BOOLEAN       DEFAULT FALSE
created_at            TIMESTAMP     DEFAULT NOW()
```

### Claims
```sql
id          SERIAL PRIMARY KEY
item_id     INTEGER  REFERENCES items(id)  NOT NULL
user_id     INTEGER  REFERENCES users(id)  NOT NULL  -- the claimant
message     TEXT     NULLABLE                         -- optional message to owner
status      VARCHAR(20)  DEFAULT 'pending'            -- 'pending', 'approved', 'rejected'
created_at  TIMESTAMP    DEFAULT NOW()
```

### Notifications
```sql
id          SERIAL PRIMARY KEY
user_id     INTEGER  REFERENCES users(id)  NOT NULL
message     TEXT     NOT NULL
is_read     BOOLEAN  DEFAULT FALSE
created_at  TIMESTAMP  DEFAULT NOW()
```

---

## 📡 API Routes

### Auth
```
POST  /api/auth/register
      Body: { name, email, password, phone, department }
      Returns: { access_token, user }
      Note: first user becomes admin automatically

POST  /api/auth/login
      Body: { email, password }
      Returns: { access_token, user }
      Error: 401 if wrong password, 403 if banned

GET   /api/auth/me
      Headers: Authorization: Bearer <token>
      Returns: { user }
      Used by frontend to restore session on page refresh

POST  /api/auth/logout
      Returns: { message }
```

### Items
```
GET   /api/items/
      Query params: status, category, search, page, per_page, my (true/false)
      Returns: { items[], total, pages, current_page }
      Note: ?my=true filters to current user's items (reads token if present)
      Cached in Redis for 5 minutes

GET   /api/items/<id>
      Returns: { id, title, description, category, status, location,
                 latitude, longitude, image_url, is_resolved,
                 created_at, posted_by, user_id, verification_question }
      Note: verification_answer is NEVER returned

POST  /api/items/
      Protected: Yes (token required)
      Content-Type: multipart/form-data
      Body: title, description, category, status, location,
            verification_question, verification_answer,
            latitude?, longitude?, image_url?, image_public_id?
      Returns: { message, item }
      Side effect: clears Redis cache

PUT   /api/items/<id>
      Protected: Yes (owner only)
      Body: JSON with any updatable fields
      Returns: { message }
      Side effect: clears Redis cache

DELETE /api/items/<id>
      Protected: Yes (owner only)
      Returns: { message }
      Side effect: clears Redis cache
```

### Claims
```
POST  /api/claims/<item_id>
      Protected: Yes (token required)
      Body: { answer, message? }
      Returns: 201 if correct answer, 400 if wrong answer
      Validation: answer checked against item.verification_answer
      Matching: partial — "pikachu" matches "pikachu keychain"
      Side effect: creates Notification for item owner
      Side effect: emits Socket.io event to owner's room

GET   /api/claims/<item_id>
      Protected: Yes (item owner only)
      Returns: { claims[] } with claimant name, email, status

PUT   /api/claims/<id>/respond
      Protected: Yes (item owner only)
      Body: { status: "approved" | "rejected" }
      Side effect: if approved → item.is_resolved = True
      Side effect: creates Notification for claimant
      Side effect: emits Socket.io event to claimant's room
      Side effect: sends email to claimant

GET   /api/claims/mine
      Protected: Yes (token required)
      Returns: { claims[] } — all claims submitted by current user
```

### Notifications
```
GET   /api/notifications/
      Protected: Yes
      Returns: { notifications[] } ordered by newest first

PUT   /api/notifications/read
      Protected: Yes
      Body: { notification_id? }
      Note: if notification_id omitted → marks ALL as read
```

### Admin (all require admin role)
```
GET   /api/admin/users
      Returns: { users[] } with is_banned and role

PUT   /api/admin/users/<id>/ban
      Toggles is_banned on user
      Returns: { message }
      Error: cannot ban admin users

GET   /api/admin/items
      Returns: { items[] } — all items across all users

DELETE /api/admin/items/<id>
      Deletes any item regardless of owner
      Side effect: clears Redis cache
      Returns: { message }

GET   /api/admin/stats
      Returns: { total_users, total_items, lost_items,
                 found_items, resolved_items, total_claims }
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL (or Supabase free account)
- Redis (or Upstash free account)
- Cloudinary free account

### Installation

```bash
# Clone the repository
git clone https://github.com/POSHANMS/lost-found-backend.git
cd lost-found-backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your_flask_secret_key
JWT_SECRET=your_jwt_signing_secret
JWT_REFRESH_SECRET=your_refresh_token_secret
REDIS_URL=rediss://default:password@host.upstash.io:6379
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
REGISTER_LIMIT=5 per minute
```

### Run Development Server

```bash
python app.py
```

API runs on `http://localhost:5000`

### Run with Docker (Recommended)

```bash
docker-compose up
```

Starts Flask + PostgreSQL + Redis with one command. No manual installs needed.

---

## 🔒 Security Features

### Rate Limiting
| Route | Limit | Reason |
|---|---|---|
| POST /api/auth/login | 10 per minute | Brute force protection |
| POST /api/auth/register | 5 per minute | Spam prevention |
| POST /api/items/ | 10 per minute | Spam prevention |

### Password Security
- bcrypt with 12 salt rounds
- Plain text password never stored or logged
- Password hash never returned in any API response
- `checkpw()` used for comparison (timing-safe)

### JWT Security
- Tokens signed with `HS256` algorithm
- Access tokens expire in 30 minutes
- Secret key loaded from environment (never hardcoded)
- Invalid/expired tokens return 401

### Input Validation
- All inputs validated with Marshmallow before touching the database
- Email format enforced
- Phone length 10-15 digits
- Password minimum 8 characters
- Category must be from allowed list (whitelist approach)

### Claim Security
- Verification answer never returned in any API response
- Answer comparison is case-insensitive
- One claim per user per item enforced at database level
- Owners cannot claim their own items

---

## 📦 Redis Caching Strategy

| Cache Key Pattern | Data | Expiry | Invalidated When |
|---|---|---|---|
| `items:page:{n}:per:{n}:status:{s}:category:{c}:search:{q}:my:{m}:user:{id}` | Item list | 5 min | Item created/updated/deleted |
| `stats` | Admin stats | 10 min | Not yet auto-invalidated |

```python
# Cache set
cache_set(key, data, expiry=300)

# Cache get
data = cache_get(key)  # returns None if expired or missing

# Cache clear (pattern)
cache_delete_pattern("items:*")  # clears all item caches
```

---

## 🔌 Socket.io Events

### Client → Server
```
Event: join
Data:  { user_id: <int> }
Action: user joins room "user_{user_id}"
```

### Server → Client
```
Event: notification
Data:  { message: <string> }
Room:  "user_{user_id}"
Triggers:
  - When someone claims your item
  - When your claim is approved or rejected
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### Test Coverage

**Auth (test_auth.py)**
- Register with valid data → 201
- Register with duplicate email → 409
- Register with invalid phone → 400
- Login with correct password → 200
- Login with wrong password → 401
- Login with banned account → 403
- Access protected route without token → 401
- Access protected route with expired token → 401

**Items (test_items.py)**
- Create item when logged in → 201
- Create item when not logged in → 401
- Get all items (public) → 200
- Get items with status filter → 200
- Get items with search → 200
- Get my items with ?my=true → 200
- Edit item as owner → 200
- Edit item as non-owner → 403
- Delete item as owner → 200

**Claims (test_claims.py)**
- Claim with correct answer → 201
- Claim with wrong answer → 400
- Claim own item → 400
- Duplicate claim → 409
- Approve claim → 200 + item resolved
- Reject claim → 200

---

## 🌐 Deployment

### Render (Backend)
1. Connect GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --worker-class eventlet -w 1 app:app`
4. Add all environment variables
5. Deploy

> **Note:** Use `eventlet` worker for Socket.io support on Render

### Supabase (Database)
1. Create free project at supabase.com
2. Copy connection string from Settings → Database
3. Add to `DATABASE_URL` environment variable
4. Run `python app.py` once to create tables with `db.create_all()`

### Upstash (Redis)
1. Create free Redis database at upstash.com
2. Copy `REDIS_URL` (starts with `rediss://`)
3. Add to environment variables

---

## 🧠 What I Learned

- Building a production-grade REST API with Flask Blueprints
- JWT authentication from scratch — encoding, decoding, middleware decorators
- Redis caching strategy — cache keys, expiry, pattern-based invalidation
- Socket.io rooms for targeted real-time notifications per user
- Marshmallow schemas for clean input validation (not manual if/else)
- Flask-Limiter for rate limiting with Redis backend
- bcrypt password hashing and timing-safe comparison
- PostgreSQL on Supabase — connection pooling, free managed hosting
- Docker and docker-compose for reproducible development environments
- Flask Blueprint pattern for organizing routes by domain
- Cloudinary integration — accepting URL from frontend, storing metadata
- Email notifications with Flask-Mail and Gmail App Passwords
- Partial string matching for flexible verification answer checking
- Cache invalidation — knowing when and what to clear

---

## 🔮 Future Improvements

- [ ] Refresh token rotation (7-day refresh token in httpOnly cookie)
- [ ] Email verification on registration
- [ ] Forgot password with time-limited reset link
- [ ] Delete image from Cloudinary when item is deleted
- [ ] Celery + Redis for async email sending (don't block API response)
- [ ] Full-text search with PostgreSQL `to_tsvector`
- [ ] API versioning (`/api/v1/`, `/api/v2/`)
- [ ] Comprehensive test coverage (90%+)
- [ ] Prometheus metrics endpoint for monitoring
- [ ] Redis pub/sub for horizontal scaling (multiple server instances)
- [ ] GraphQL API as alternative to REST
- [ ] S3 as Cloudinary alternative
- [ ] Webhook support for external integrations
- [ ] Item expiry — auto-mark unresolved items after 30 days
- [ ] Audit log — track all admin actions

---

## 👨‍💻 Author

**Poshan M S**
Full Stack Developer
[GitHub](https://github.com/POSHANMS)

---

## 📝 License

MIT License — feel free to use this project for learning purposes.