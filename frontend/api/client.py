import requests

from config import settings

BASE_URL = settings.base_url
USER_ID = settings.user_id


def _api(method: str, path: str, **kwargs):
    url = f"{BASE_URL}{path}"
    resp = requests.request(method, url, timeout=10, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _normalize_task(task: dict) -> dict:
    """Add label_ids list extracted from the labels objects returned by the backend."""
    task["label_ids"] = [lb["id"] for lb in task.get("labels", [])]
    return task


def get_projects():
    return _api("GET", "/projects/", params={"user_id": USER_ID})


def create_project(name: str, description: str = ""):
    return _api("POST", "/projects/", params={"user_id": USER_ID},
                json={"name": name, "description": description})


def update_project(project_id: int, name: str, description: str):
    return _api("PUT", f"/projects/{project_id}",
                json={"name": name, "description": description})


def delete_project(project_id: int):
    return _api("DELETE", f"/projects/{project_id}")


# ─── Tasks ────────────────────────────────────────────────────────────────────

def get_tasks(project_id: int = None, status: str = None, label_id: int = None):
    params = {}
    if status:
        params["status"] = status
    if label_id:
        params["label_id"] = label_id

    if project_id:
        tasks = _api("GET", f"/projects/{project_id}/tasks", params=params)
    else:
        # No global "all tasks" endpoint — collect from every project
        projects = get_projects()
        tasks = []
        for p in projects:
            tasks.extend(_api("GET", f"/projects/{p['id']}/tasks", params=params))

    return [_normalize_task(t) for t in tasks]


def create_task(project_id: int, title: str, description: str = "",
                deadline: str = None, label_ids: list = None):
    body = {"title": title, "description": description,
            "deadline": deadline, "label_ids": label_ids or []}
    return _normalize_task(_api("POST", f"/projects/{project_id}/tasks", json=body))


def update_task(task_id: int, **fields):
    return _normalize_task(_api("PUT", f"/tasks/{task_id}", json=fields))


def delete_task(task_id: int):
    return _api("DELETE", f"/tasks/{task_id}")


# ─── Labels ───────────────────────────────────────────────────────────────────

def get_labels():
    return _api("GET", "/labels/", params={"user_id": USER_ID})


def create_label(name: str, color: str = "#185FA5"):
    return _api("POST", "/labels/", params={"user_id": USER_ID},
                json={"name": name, "color": color})


def delete_label(label_id: int):
    return _api("DELETE", f"/labels/{label_id}")


# ─── Dashboard ────────────────────────────────────────────────────────────────

def get_dashboard_summary():
    summary = _api("GET", "/dashboard/summary", params={"user_id": USER_ID})
    overdue = get_overdue_tasks()
    summary["overdue"] = len(overdue)
    return summary


def get_overdue_tasks():
    result = _api("GET", "/dashboard/overdue", params={"user_id": USER_ID})
    return result["tasks"]


def get_project_progress(project_id: int):
    prog = _api("GET", f"/dashboard/projects/{project_id}/progress")
    prog["percent"] = prog.get("percent_done", 0)
    return prog
