from datetime import datetime, timezone
from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Project, User
from schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_project_or_404(project_id: int, db: Session) -> Project:
    """Return an active (non-deleted) project, or raise 404."""
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


@router.get("/", response_model=List[ProjectResponse])
def list_projects(user_id: int, db: Session = Depends(get_db)):
    """
    Return all non-deleted projects for the given user.
    user_id is passed as a query param for now; will be derived from JWT once auth is added.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return (
        db.query(Project)
        .filter(
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
        )
        .all()
    )


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(user_id: int, body: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project for the user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    project = Project(**body.model_dump(), user_id=user_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Return a single project by ID."""
    return _get_project_or_404(project_id, db)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, body: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project's name or description."""
    project = _get_project_or_404(project_id, db)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=200)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Soft-delete: sets deleted_at, preserves the underlying data."""
    project = _get_project_or_404(project_id, db)
    project.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Project moved to trash."}
