# API Documentation

Base URL (local development): `http://localhost:8000/api`

All responses use a consistent envelope:

**Success**
```json
{ "success": true, "message": "...", "data": { ... } }
```

**Error**
```json
{ "success": false, "message": "...", "errors": { ... } }
```

Authenticated endpoints require an `Authorization: Bearer <access_token>` header.

---

## Health

### `GET /api/health/`
Auth: none.
Returns `{"success": true, "message": "API is running"}`.

---

## Auth

### `POST /api/auth/register/`
Auth: none.

Request body:
```json
{ "name": "Manavi", "email": "manavi@example.com", "password": "Passw0rd1" }
```
Rules: name required; valid email required and must be unique; password must be 8+ characters with at least one letter and one number.

Success `201`:
```json
{ "success": true, "message": "User registered successfully",
  "data": { "id": "...", "name": "Manavi", "email": "manavi@example.com", "created_at": "..." } }
```

Error `400` (duplicate email or validation failure):
```json
{ "success": false, "message": "Validation failed", "errors": { "email": ["A user with this email already exists."] } }
```

### `POST /api/auth/login/`
Auth: none.

Request body: `{ "email": "...", "password": "..." }`

Success `200`:
```json
{ "success": true, "message": "Login successful",
  "data": { "access": "<jwt>", "refresh": "<jwt>", "user": { "id": "...", "name": "...", "email": "..." } } }
```

Error `401`: `{ "success": false, "message": "Invalid email or password.", "errors": {} }`

### `POST /api/auth/refresh/`
Auth: none (uses the refresh token itself as the credential).

Request body: `{ "refresh": "<jwt>" }`

Success `200`: `{ "success": true, "message": "Token refreshed", "data": { "access": "<jwt>" } }`

Error `401`: expired, invalid, or revoked refresh token.

### `POST /api/auth/logout/`
Auth: none required (only a valid refresh token is needed, so a client can log out even if its access token already expired).

Request body: `{ "refresh": "<jwt>" }`

Success `200`: `{ "success": true, "message": "Logged out successfully", "data": null }`. Revokes the refresh token so it can no longer be used to get new access tokens.

### `GET /api/auth/me/`
Auth: required.

Success `200`:
```json
{ "success": true, "message": "Success", "data": { "id": "...", "name": "...", "email": "..." } }
```

Error `401`: missing/invalid/expired token.

---

## Tasks

Every task endpoint requires authentication. A task is only visible to (and
editable/deletable by) the user who created it or the user it is assigned
to; any other user gets `403 Forbidden`.

### `GET /api/tasks/`
Auth: required.

Query parameters (all optional):
| Param | Description |
|---|---|
| `status` | `TODO` \| `IN_PROGRESS` \| `COMPLETED` |
| `priority` | `LOW` \| `MEDIUM` \| `HIGH` |
| `search` | Case-insensitive match against title or description |
| `ordering` | `created_at`, `-created_at`, `updated_at`, `due_date`, `priority`, `title`, `status` (prefix `-` for descending) |
| `page` | Page number, default 1 |
| `page_size` | Items per page, default 10, max 100 |

Success `200`:
```json
{ "success": true, "message": "Success",
  "data": {
    "results": [ { "id": "...", "title": "...", "description": "...", "status": "TODO",
                   "priority": "HIGH", "due_date": "2026-09-20", "created_by": "...",
                   "assigned_to": null, "created_at": "...", "updated_at": "..." } ],
    "count": 1, "num_pages": 1, "current_page": 1, "page_size": 10,
    "next": null, "previous": null
  } }
```

### `POST /api/tasks/`
Auth: required.

Request body:
```json
{ "title": "Write report", "description": "Q3 summary", "status": "TODO",
  "priority": "HIGH", "due_date": "2026-09-20", "assigned_to": null }
```
Only `title` is required; other fields default to `status=TODO`, `priority=MEDIUM`.

Success `201`: task object, as above. Error `400`: validation errors (e.g. blank title, invalid status/priority).

### `GET /api/tasks/<id>/`
Auth: required (owner or assignee only).

Success `200`: task object. Error `400` invalid ID format, `404` not found, `403` not owner/assignee.

### `PUT /api/tasks/<id>/`
Full update - same body shape as create; all fields expected. Same auth/error rules as `GET`.

### `PATCH /api/tasks/<id>/`
Partial update - only send the fields you want to change. Same auth/error rules as `GET`.

### `PATCH /api/tasks/<id>/status/`
Auth: required (owner or assignee only).

Request body: `{ "status": "IN_PROGRESS" }`

Success `200`: updated task object. Error `400` invalid status value.

### `DELETE /api/tasks/<id>/`
Auth: required (owner or assignee only).

Success `200`: `{ "success": true, "message": "Task deleted successfully", "data": null }`.

### `GET /api/tasks/stats/`
Auth: required. Powers the dashboard.

Success `200`:
```json
{ "success": true, "message": "Success",
  "data": { "total": 5, "todo": 2, "in_progress": 2, "completed": 1, "high_priority_open": 1 } }
```
`high_priority_open` counts tasks with `priority=HIGH` that are not `COMPLETED`.

---

## Common error responses

| Status | Meaning |
|---|---|
| 400 | Validation failed, or a malformed task ID |
| 401 | Missing, invalid, or expired token; wrong login credentials |
| 403 | Authenticated, but not the owner/assignee of the resource |
| 404 | Resource does not exist |
| 500 | Unexpected server error (details are logged server-side, never returned to the client) |
