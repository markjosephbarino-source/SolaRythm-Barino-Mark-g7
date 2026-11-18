# SolaRythm

Full Stack Django project (PostgreSQL / Supabase). This phase: **Account Feature**
(registration, login/logout, role-based dashboards, user profile).

## Setup
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # then fill in your PostgreSQL / Supabase credentials
python manage.py migrate
python manage.py createsuperuser # superusers automatically get the Admin role
python manage.py runserver
```

## Roles
| Role | Dashboard URL | Notes |
|------|---------------|-------|
| Member | `/dashboard/member/` | Default for every sign-up |
| Admin  | `/dashboard/admin/`  | Set via `createsuperuser` or in `/admin` |

Opening the other role's dashboard returns **403 Forbidden**; logged-out users are sent to the login page.

## Main URLs
`/accounts/signup/` `/accounts/login/` `/accounts/logout/` (POST) `/accounts/profile/` `/accounts/profile/edit/`

## Tests
`python manage.py test`
