from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Label, User
from schemas import LabelCreate, LabelResponse, LabelUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/labels", tags=["Labels"])


def _get_label_or_404(label_id: int, db: Session) -> Label:
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found.")
    return label


@router.get("/", response_model=List[LabelResponse])
def list_labels(user_id: int, db: Session = Depends(get_db)):
    """Return all labels belonging to the user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db.query(Label).filter(Label.user_id == user_id).all()


@router.post("/", response_model=LabelResponse, status_code=201)
def create_label(user_id: int, body: LabelCreate, db: Session = Depends(get_db)):
    """Create a new label."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    label = Label(**body.model_dump(), user_id=user_id)
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


@router.put("/{label_id}", response_model=LabelResponse)
def update_label(label_id: int, body: LabelUpdate, db: Session = Depends(get_db)):
    """Update a label's name or color."""
    label = _get_label_or_404(label_id, db)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(label, field, value)

    db.commit()
    db.refresh(label)
    return label


@router.delete("/{label_id}", status_code=200)
def delete_label(label_id: int, db: Session = Depends(get_db)):
    """
    Hard-delete a label.
    Related task_labels rows are removed automatically via ON DELETE CASCADE.
    """
    label = _get_label_or_404(label_id, db)
    db.delete(label)
    db.commit()
    return {"message": "Label deleted successfully."}
