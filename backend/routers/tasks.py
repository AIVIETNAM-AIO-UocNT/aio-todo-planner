from datetime import datetime, timezone
from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Label, Project, Task
from schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from sqlalchemy.orm import Session

router = APIRouter(tags=["Tasks"])


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.deleted_at.is_(None),
        )
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or has been deleted.")
    return task


def _get_project_or_404(project_id: int, db: Session) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or has been deleted.")
    return project


def _resolve_labels(label_ids: List[int], db: Session) -> List[Label]:
    """Resolve a list of label IDs to Label objects; raises 404 if any ID is missing."""
    if not label_ids:
        return []
    labels = db.query(Label).filter(Label.id.in_(label_ids)).all()
    found_ids = {label.id for label in labels}
    missing = set(label_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Labels not found: {sorted(missing)}",
        )
    return labels


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    project_id: int,
    status: Optional[TaskStatus] = None,
    label_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Return all tasks for a project. Optional filters:
    - status: todo | doing | done
    - label_id: only tasks assigned to this label
    """
    _get_project_or_404(project_id, db)

    query = db.query(Task).filter(
        Task.project_id == project_id,
        Task.deleted_at.is_(None),
    )

    if status:
        query = query.filter(Task.status == status)

    if label_id:
        query = query.filter(Task.labels.any(Label.id == label_id))

    return query.all()


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201)
def create_task(project_id: int, body: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task in the project. label_ids lists the labels to attach."""
    _get_project_or_404(project_id, db)

    labels = _resolve_labels(body.label_ids, db)

    task = Task(
        project_id=project_id,
        title=body.title,
        description=body.description,
        deadline=body.deadline,
        status=body.status,
    )
    task.labels = labels

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Return a single task by ID."""
    return _get_task_or_404(task_id, db)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task. If label_ids is provided, it replaces all existing labels.
    If label_ids is omitted (None), existing labels are left unchanged.
    """
    task = _get_task_or_404(task_id, db)

    update_data = body.model_dump(exclude_unset=True)
    label_ids = update_data.pop("label_ids", None)

    for field, value in update_data.items():
        setattr(task, field, value)

    if label_ids is not None:
        task.labels = _resolve_labels(label_ids, db)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Soft-delete a task."""
    task = _get_task_or_404(task_id, db)
    task.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Task deleted successfully."}
