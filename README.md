# RiderGuard

An independent companion app for Filipino ride-hailing and delivery riders: log trips, check fares against published
commission rates, and keep a timestamped evidence vault for disputes.

IT317 · G7 · Kazt Andre S. Ovalo

**Stack:** Full-stack Django (templates) · PostgreSQL on Supabase

## Phase 1: Account feature

| Requirement | Where |
|---|---|
| Registration with validation (required fields, email format, unique username/email, matching passwords) | `accounts/forms.py` → `RegistrationForm` |
| Hashed passwords via Django auth | Custom `User` model extends `AbstractUser` |
| Login (username **or** email) / logout | `accounts/views.py`, `accounts/backends.py` |
| Protected pages redirect to login | `@login_required` / `@role_required` |
| Two roles: **Rider** and **Admin**, each with its own dashboard | `/dashboard/rider/`, `/dashboard/admin/` |
| Blocking another role's dashboard by URL | `accounts/decorators.py` → `role_required` |
| View/edit own profile (name, email, contact number, photo, platforms, vehicle) | `/profile/`, `/profile/edit/` |

Public registration always creates a **Rider**. Admins are created with `createsuperuser` (or promoted in Django admin).

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # then fill in SECRET_KEY and DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`DATABASE_URL` is your Supabase connection string (Project Settings → Database → Connection string → URI).
Use the **Session pooler** string if your network has no IPv6.

## Tests

```bash
python manage.py test accounts
```

## Roadmap

| Sprint | Module |
|---|---|
| 3 | Trip Logger, Dashboard summary |
| 4 | Fare Checker |
| 5 | Dispute Vault, Rights & Resources Hub |
| 6 | Community Reports, pilot |
