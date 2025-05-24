# Kanban Backend – Django REST API

This project is the backend for a kanban-style task management app.  
It uses Django, Django REST Framework, and token authentication.

---

## 🔧 Setup

1. Clone the repository:

```bash
git clone https://github.com/NoAltF4Dan/kanban_backend.git
cd kanban_backend
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file and add:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

> You can generate a new Django secret key using https://djecrety.ir/

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Start the server:

```bash
python manage.py runserver
```

---

## 🚀 API Endpoints

All routes are prefixed with `/api/`

- `POST /api/registration/` – Register user
- `POST /api/login/` – Login and get token
- `GET /api/boards/` – List boards
- `POST /api/boards/` – Create board
- `GET /api/boards/<id>/` – Board detail with tasks
- `PATCH /api/boards/<id>/` – Update members
- `DELETE /api/boards/<id>/` – Delete board
- `POST /api/tasks/` – Create task
- `GET /api/tasks/assigned-to-me/` – Tasks assigned to current user
- `GET /api/tasks/reviewing/` – Tasks where user is reviewer
- `GET /api/tasks/<id>/comments/` – List task comments
- `POST /api/tasks/<id>/comments/add/` – Add comment
- `DELETE /api/tasks/<task_id>/comments/<comment_id>/` – Delete comment
- `GET /api/email-check/?email=example@example.com` – Check if user exists

> Full API behavior based on project documentation (see provided PDF).

---

## 👤 Example Login (for testing)

After running `createsuperuser`, use the admin panel at:

```
http://127.0.0.1:8000/admin/
```

Login with your superuser credentials and create test users, boards, columns, and tasks.

---

## 📂 Notes

- Database (`db.sqlite3`) is not included in Git
- Frontend is not part of this repository
- CORS is enabled via `django-cors-headers`
