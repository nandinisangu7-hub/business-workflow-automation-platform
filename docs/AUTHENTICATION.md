# Authentication and authorization

The API uses password-based registration plus expiring bearer JWTs. Passwords are bcrypt-hashed and are never returned by an API response or embedded in a token.

- `POST /api/v1/auth/register` accepts `email`, `full_name`, and an 8–128 character password. New registrations always receive the `employee` role.
- `POST /api/v1/auth/login` uses OAuth2 form fields (`username` is the email) and returns an access token plus safe user data.
- `GET /api/v1/auth/me` requires `Authorization: Bearer <token>`.

`get_current_user` validates token signature, expiry, user existence, and active status. `require_roles(...)` is the reusable server-side RBAC guard for later manager/admin routes.

## Local seed data

Run migrations first, then:

```powershell
$env:SEED_PASSWORD = 'a-long-local-password'
cd backend
python scripts/seed_users.py
```

This creates `admin@example.local`, `manager@example.local`, and `employee@example.local`, assigns the employee to the manager, is idempotent, and never supplies or resets passwords automatically.
