# Task Management System

A full-stack task management application: React frontend, Django + Django
REST Framework backend, MongoDB for all application data, and JWT
authentication.

## Overview

Users can register, log in, and manage their own tasks: create, view,
update, delete, change status, search, filter, sort, and paginate through
them. A dashboard summarizes task counts at a glance. Every task is
private to its creator (and, if set, its assignee) - no one else can see
or modify it.

## Features

- Registration, login, logout, JWT access/refresh tokens, "current user" endpoint
- Full task CRUD, plus a dedicated status-change endpoint
- Search (title/description), filter (status, priority), sort, pagination
- Dashboard with task counts by status and open high-priority tasks
- Ownership/assignment-based authorization on every task endpoint
- Consistent `{success, message, data}` / `{success, message, errors}` API responses
- Centralized error handling - internal errors are never leaked to the client
- Frontend: protected routes, automatic access-token refresh on 401, loading/empty/error states, delete confirmation
- 39 backend tests (unit + API + full-flow integration) and 21 frontend tests, all passing

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Axios, Vite |
| Backend | Django 6, Django REST Framework |
| Database | MongoDB (via PyMongo) |
| Auth | JWT (PyJWT), password hashing via Django's hasher |
| Frontend tests | Vitest, React Testing Library |
| Backend tests | Django's test runner, `mongomock` for a DB-free test environment |

## Architecture

The backend deliberately does **not** use Django's ORM or `django.contrib.auth`
for application data - there is no SQL database involved in storing users
or tasks. All reads/writes go through PyMongo directly (see
`backend/apps/common/mongo.py`). Django's own request/response cycle, DRF's
serializers/views/pagination, and JWT auth are still used - only the data
layer is MongoDB instead of the ORM. See the "Deployment Preparation"
section below and the code comments in `apps/common/mongo.py` for why an
in-memory SQLite database still appears in settings (it exists only for
Django's internal test-runner plumbing, and holds zero application data).

## Folder structure

```
task-management-system/
├── README.md
├── API_DOCUMENTATION.md
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── project/
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── common/        # mongo connection, JWT utils, auth class, responses, exceptions, pagination
│   │   ├── users/         # register/login/logout/refresh/me
│   │   └── tasks/         # task CRUD, status, stats
│   └── tests/             # unit, API, and integration tests
└── frontend/
    ├── .env.example
    ├── src/
    │   ├── components/    # ui/ (generic) and tasks/ (task-specific)
    │   ├── pages/
    │   ├── layouts/       # AppLayout (sidebar), AuthLayout (login/register)
    │   ├── hooks/         # useAuth, useTasks, useFetch, useDebounce
    │   ├── services/      # api.js (Axios instance), authService, taskService
    │   ├── utils/         # constants, validators, date formatting
    │   ├── context/       # AuthContext
    │   ├── routes/        # ProtectedRoute
    │   └── App.jsx
    └── vite.config.js
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A running MongoDB instance (local install, or `mongodb-memory-server`/`mongomock` for testing - see note below)

## MongoDB configuration

By default the backend connects to `mongodb://localhost:27017` and uses
database `intern_db` (both configurable via `.env`). If you don't have
MongoDB installed locally, the quickest option is MongoDB Community
Server, or Atlas's free tier - point `MONGO_URI` at either.

> **Sandbox note:** this project was developed and tested in an environment
> with no ability to install or run a real `mongod` process, so the
> automated test suite uses `mongomock` (an in-memory, API-compatible fake)
> instead of a live MongoDB server. The application code talks to Mongo
> through the same `pymongo` calls either way, so pointing `MONGO_URI` at a
> real MongoDB instance is a configuration change, not a code change.

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env: set SECRET_KEY, JWT_SECRET_KEY, MONGO_URI
python3 manage.py runserver
```

The API is now available at `http://localhost:8000/api/`.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env            # set VITE_API_URL if the backend isn't on localhost:8000
npm run dev
```

The app is now available at `http://localhost:5173`.

## Environment variables

**Backend (`backend/.env`)**
```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=intern_db
JWT_SECRET_KEY=
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

**Frontend (`frontend/.env`)**
```
VITE_API_URL=http://localhost:8000/api
```

Never commit real `.env` files - only the `.env.example` templates are checked in.

## Running tests

**Backend** (from `backend/`):
```bash
python3 manage.py test tests
```
Runs 39 tests: registration, login (valid/invalid), JWT auth, unauthorized
access, task CRUD, invalid task IDs, validation, authorization
(owner/assignee-only), filtering, searching, pagination, dashboard stats,
and two full end-to-end flow tests (register → login → create → update →
change status → search/filter → delete → logout, plus a cross-user
authorization check).

**Frontend** (from `frontend/`):
```bash
npm test
```
Runs 21 tests covering the login and registration forms (validation,
success, and server-error paths), the task form (validation, submit,
pre-fill, error surfacing), the task list page (loading/empty/error
states, delete confirmation, status change), protected-route redirects,
and API error-message extraction.

## API documentation

See [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) for every endpoint:
method, URL, auth requirement, request body, and both success and error
response shapes.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Backend won't start / import errors | Virtualenv not activated, or `pip install -r requirements.txt` not run |
| `401` on every request from the frontend | `VITE_API_URL` wrong, or the access token expired and the refresh token is also invalid/missing - log in again |
| CORS errors in the browser console | Frontend origin not listed in `CORS_ALLOWED_ORIGINS` in the backend `.env` |
| Registration always fails with "already exists" | You're hitting a database that already has that email - use a different email or drop the `users` collection |
| Backend can't reach MongoDB | Check `MONGO_URI`/`MONGO_DB_NAME`, and that `mongod` is actually running and reachable |
| Frontend shows a blank page | Check the browser console; most commonly a missing/incorrect `VITE_API_URL` |

## Deployment Preparation

Docker, AWS, and CI/CD were intentionally **not** implemented here - they're
being handled manually. This project is structured to make that
straightforward:

- **No hardcoded config** - both apps read all environment-specific values
  (URLs, secrets, DB connection info) from environment variables, so a
  Dockerfile just needs to supply a `.env` or equivalent env vars.
- **Backend and frontend are independent services** with their own
  dependency manifests (`requirements.txt`, `package.json`), which maps
  cleanly onto two separate Docker images/containers.
- **`.env.example` files exist for both apps** listing every variable
  a `docker-compose.yml` or ECS/EC2 task definition will need to set.
- **CORS is already configurable**, so once the frontend gets a real
  domain/port (behind Docker/EC2/CloudFront), just update
  `CORS_ALLOWED_ORIGINS`.

What's left for you to do manually, as planned:

- **Docker**: write Dockerfiles for `backend/` and `frontend/`, and a
  `docker-compose.yml` that also runs a `mongo` container, wiring
  `MONGO_URI` to that service's hostname.
- **AWS**: provision EC2 (or ECS), configure Security Groups (open 80/443,
  restrict DB access), set up S3 if you want static asset hosting for the
  built frontend, IAM roles/policies, and CloudWatch for logs/metrics.
- **CI/CD**: a GitHub Actions workflow that runs `python3 manage.py test`
  and `npm test` on every push, then builds and pushes Docker images
  (Docker Hub or ECR) and deploys to EC2/ECS on merge to main.

Nothing above has been implemented in this repository - it's scoped
entirely to you, as requested.
