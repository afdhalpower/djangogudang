# Warehouse Inventory Management System

A modern, professional warehouse inventory management system built with Django 5 — designed for small-to-medium businesses.

## Learning Mode

Built feature-by-feature as a teaching project for a Laravel developer transitioning to Django. Every commit includes architecture decisions, Django best practices, and Laravel analogies.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 + Django ORM |
| Database | SQLite (dev, default) / PostgreSQL (production — switch via `DB_ENGINE=postgres`) |
| Auth | Django Authentication + Custom User Model (role-based) |
| Admin | Django Admin (configured for usability) |
| Frontend | Django Templates + Tailwind CSS (npm build) + HTMX + Alpine.js |

## Features

### ✅ Done

- [x] **Project Foundation** — multi-app structure, settings with SQLite/PostgreSQL toggle, .gitignore, requirements
- [x] **Authentication** — Login/Logout (POST+CSRF), Change Password, User Profile
- [x] **User Roles** — Administrator, Warehouse Staff (via custom `User.role` field)
- [x] **Django Admin** — beautiful admin with filters, search, ordering, custom fieldsets
- [x] **UI Shell** — sidebar + topbar layout, Tailwind build via npm, HTMX + Alpine.js locally served, responsive, ERP-style
- [x] **Categories** — full CRUD (List + pagination, Detail, Create, Update, Delete)
- [x] **Units** — full CRUD (name + abbreviation; seeded: pcs, box, kg, liter, pack, m, roll, set)
- [x] **Suppliers** — full CRUD (company name, contact person, phone, email, address)
- [x] **Products** — CRUD with SKU, barcode, image, category FK, unit FK, supplier FK, price, stock, search/filter/pagination, N+1 prevention (select_related)
- [x] **Stock In** — multi-line form, auto-increase stock via signal, atomic transactions
- [x] **Stock Out** — multi-line form, auto-decrease stock, negative stock prevention (rollback)
- [ ] **Stock Adjustment** — manual adjust with reason (lost/damaged/expired/correction)
- [ ] **Transaction History** — complete movement history with filters
- [x] **Dashboard** — 5 stat cards (total, low stock, inactive, in/out today), low-stock table, recent activity
- [ ] **Reports** — inventory report, low stock report, stock card, CSV/Excel/PDF export
- [ ] **Notifications** — low stock warning, dashboard alert
- [ ] **Global Search** — search products, suppliers, transactions
- [ ] **Settings** — company profile, warehouse information, system settings

## Quick Start

```bash
# Clone & enter
git clone https://github.com/afdhalpower/djangogudang.git
cd djangogudang

# Setup Python environment
/usr/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup Tailwind CSS
cd tailwind
npm install
npm run build
cd ..

# Database & superuser
python manage.py migrate
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in.

### Switch to PostgreSQL

Copy `.env.example` to `.env`, set `DB_ENGINE=postgres` and fill the PostgreSQL credentials. That's it — Django picks it up automatically.

## Project Structure

```
djangogudang/
├── config/           # Project package (settings, urls, wsgi, asgi)
├── accounts/         # Custom User model, auth views, profile
├── dashboard/        # Home page (post-login landing)
├── categories/       # Product categories CRUD
├── units/            # Measurement units CRUD
├── templates/        # Global + per-app templates
├── tailwind/         # Tailwind CSS source (npm)
├── static/           # Built CSS + vendor JS (HTMX, Alpine)
└── manage.py         # Django CLI (like artisan)
```

## License

Private project — Afdhal RZ
