# Django Expense Tracker

A simple personal expense tracker built with Django. Users sign up, record their spending in KES, and see a monthly summary by category.

## Features
- User sign up, log in, and log out
- Add, edit, and delete expenses (title, amount, category, date, note)
- Users only see and change their own expenses
- Monthly summary with total spent and a per-category breakdown
- Previous/next month navigation
- Django admin for management
- Automated tests

## Tech Stack
- Python 3
- Django
- SQLite (default database)

## Getting Started

```bash
git clone https://github.com/CodeNova55/django-expense-tracker.git
cd django-expense-tracker
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000

## Running Tests

```bash
python manage.py test
```

## Project Structure

```
config/                  project settings and root URLs
expenses/models.py       Expense model
expenses/views.py        CRUD views, signup, and monthly summary
expenses/forms.py        expense form
expenses/tests.py        automated tests
```

## Git Workflow
- One feature branch per piece of work
- Feature branch -> PR into `develop`
- `develop` -> PR into `main` (after approval)
- No direct pushes to `develop` or `main`

## Roadmap
- Monthly budgets and alerts
- Charts and CSV export
- Deployment