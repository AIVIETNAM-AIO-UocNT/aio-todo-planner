# AIO Todo Planner — Backend

REST API for the AIO Conquer 2026 task management application, built with **FastAPI** + **SQLAlchemy** + **MySQL**.
---

## Project Structure

```
backend/
├── main.py            # FastAPI app entry point, user endpoints
├── database.py        # SQLAlchemy engine + session + Base
├── config.py          # Environment settings (pydantic-settings)
├── init_db.py         # One-time table creation script
├── models/
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   ├── label.py
│   └── task_label.py  # Many-to-many join table
├── schemas/
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   └── label.py
└── routers/
    ├── projects.py
    ├── tasks.py
    ├── labels.py
    └── dashboard.py
```

---

## Setup & Run

### 1. Create the `.env` file

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<database>
DB_ECHO=False
```

Example:

```env
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/todo_planner
DB_ECHO=False
```

### 2. Install dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using **pip** with a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Initialize the database

Run this **once** to create all tables in MySQL:

```bash
python init_db.py
```

> For schema changes after the initial setup, use **Alembic** instead of re-running this script.

### 4. Start the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API Docs

Once the server is running, open the interactive docs in your browser:

| UI      | URL                                  |
|---------|--------------------------------------|
| Swagger | http://localhost:8000/docs           |
| ReDoc   | http://localhost:8000/redoc          |

---

## API Overview

| Method | Endpoint                              | Description                        |
|--------|---------------------------------------|------------------------------------|
| POST   | `/users`                              | Create a new user                  |
| GET    | `/users/{user_id}`                    | Get user by ID                     |
| GET    | `/projects`                           | List projects for a user           |
| POST   | `/projects`                           | Create a project                   |
| PUT    | `/projects/{id}`                      | Update a project                   |
| DELETE | `/projects/{id}`                      | Soft-delete a project              |
| GET    | `/projects/{id}/tasks`                | List tasks in a project            |
| POST   | `/projects/{id}/tasks`                | Create a task                      |
| GET    | `/tasks/{id}`                         | Get task by ID                     |
| PUT    | `/tasks/{id}`                         | Update a task                      |
| DELETE | `/tasks/{id}`                         | Soft-delete a task                 |
| GET    | `/labels`                             | List labels for a user             |
| POST   | `/labels`                             | Create a label                     |
| PUT    | `/labels/{id}`                        | Update a label                     |
| DELETE | `/labels/{id}`                        | Hard-delete a label                |
| GET    | `/dashboard/summary`                  | Task count by status               |
| GET    | `/dashboard/overdue`                  | Overdue tasks                      |
| GET    | `/dashboard/projects/{id}/progress`   | Project completion percentage      |
| GET    | `/health`                             | Health check                       |
