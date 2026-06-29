from datetime import date

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from models import Project, Task, User
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(user_id: int, db: Session = Depends(get_db)):
    """
    Task summary for a user:
    - Task count per status (todo / doing / done)
    - Total task count
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    logger.debug(f"Fetching task summary for user_id={user_id}")

    rows = (
        db.query(Task.status, func.count(Task.id).label("count"))
        .join(Project, Task.project_id == Project.id)
        .filter(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
            Task.deleted_at.is_(None),
        )
        .group_by(Task.status)
        .all()
    )

    counts = {"todo": 0, "doing": 0, "done": 0}
    for status, count in rows:
        counts[status] = count

    return {
        "total": sum(counts.values()),
        "todo": counts["todo"],
        "doing": counts["doing"],
        "done": counts["done"],
    }


@router.get("/overdue")
def overdue_tasks(user_id: int, db: Session = Depends(get_db)):
    """Tasks past their deadline that are not yet done."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    today = date.today()
    logger.debug(f"Fetching overdue tasks for user_id={user_id} as of {today}")

    tasks = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
            Task.deleted_at.is_(None),
            Task.deadline < today,
            Task.status != "done",
        )
        .all()
    )

    return {
        "count": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "deadline": t.deadline,
                "status": t.status,
                "project_id": t.project_id,
            }
            for t in tasks
        ],
    }


@router.get("/projects/{project_id}/progress")
def project_progress(project_id: int, db: Session = Depends(get_db)):
    """Project progress: done tasks / total tasks, returned as a percentage."""
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    logger.debug(f"Fetching progress for project_id={project_id}")

    rows = (
        db.query(Task.status, func.count(Task.id).label("count"))
        .filter(
            Task.project_id == project_id,
            Task.deleted_at.is_(None),
        )
        .group_by(Task.status)
        .all()
    )

    counts = {"todo": 0, "doing": 0, "done": 0}
    for status, count in rows:
        counts[status] = count

    total = sum(counts.values())
    percent_done = round(counts["done"] / total * 100, 1) if total > 0 else 0.0

    return {
        "project_id": project_id,
        "project_name": project.name,
        "total": total,
        "todo": counts["todo"],
        "doing": counts["doing"],
        "done": counts["done"],
        "percent_done": percent_done,
    }
