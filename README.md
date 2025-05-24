Kanban Backend API – KanMind 🧠📦
This is the backend for a Kanban-style project management app, built using Django and Django REST Framework (DRF).

🚀 Features
User registration & authentication

Boards with multiple columns

Tasks assigned to users

REST API with full CRUD support

Permissions: only owners can edit their content

95%+ test coverage (target)

🛠️ Setup Instructions
Clone the repository

git clone git@github.com:NoAltF4Dan/kanban-backend.git
cd kanban-backend

Create virtual environment and activate it

python3 -m venv venv
source venv/bin/activate

Install requirements

pip install -r requirements.txt

Apply migrations

python manage.py migrate

Create superuser

python manage.py createsuperuser

Run development server

python manage.py runserver

🔗 API Endpoints
Base URL: http://localhost:8000/api/

Resource	URL
Boards	/api/boards/
Columns	/api/columns/
Tasks	/api/tasks/

📦 Notes
Do not commit your SQLite DB or .env file

Make sure .gitignore includes:

venv/

*.sqlite3

pycache/

.vscode/

## ✅ Test Coverage

- Total Coverage: **93%**
- All critical features (authentication, board access, CRUD) covered
- Permissions are fully tested

---

## ✅ Final Project Status

- Backend vollständig mit Django + DRF umgesetzt
- Full CRUD für Boards, Columns, Tasks und Comments
- Zugriffsschutz (nur Owner kann bearbeiten) aktiv
- Zusätzliche Features:
  - 🟡 Task-Prioritäten mit `high/medium/low`
  - 💬 Kommentare zu Tasks
  - 🔢 Spalten zeigen Anzahl an High-Priority-Tasks
- Testabdeckung: **93 %**
- Clean Code: ✔️ `PEP8`, ✔️ `14-Zeilen-Regel`, ✔️ keine Leichen im Code

---

## 🧠 Hinweise

- Frontend wird extern bereitgestellt
- Backend läuft unabhängig auf Port 8000
- Datenbank `.sqlite3` ist **nicht** versioniert (`.gitignore`)
- README & Codebase auf Englisch, Kommentare und Struktur DRF-konform

---

## 🧪 Test it

```bash
python manage.py test
coverage run manage.py test
coverage report

👤 Author
Daniel aka NoAltF4Dan
Backend-Projekt im Rahmen der Developer Akademie
Mai 2025 – deployed, getestet, dokumentiert ✅
