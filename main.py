from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import func 
import database
from models import (
    user as user_model,
    project as project_model,
    task as task_model,
    task_label as task_label_model,
    label as label_model
)

from schemas import (
    user as user_schema,
    project as project_schema,
    task as task_schema,
    label as label_schema
)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db 
    finally:
        db.close() 


# PHẦN 1: API CHO USER
@app.post("/users/", response_model=user_schema.UserResponse)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    new_user = user_model.User(
        username=user.username,
        email=user.email,
        password_hash=user.password
    )
    db.add(new_user)     
    db.commit()         
    db.refresh(new_user)  
    return new_user

# PHẦN 2: API CHO PROJECT 
@app.post("/users/{user_id}/projects/", response_model=project_schema.ProjectResponse)
def create_project(user_id: int, project: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    new_project = project_model.Project(**project.model_dump(), user_id=user_id)
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/users/{user_id}/projects/", response_model=List[project_schema.ProjectResponse])
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    projects = db.query(project_model.Project).filter(
        project_model.Project.user_id == user_id,
        project_model.Project.deleted_at.is_(None)
    ).all()
    return projects


@app.get("/projects/{project_id}", response_model=project_schema.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.deleted_at.is_(None)
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    return project

@app.put("/projects/{project_id}", response_model=project_schema.ProjectResponse)
def update_project(project_id: int, project_update: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.deleted_at.is_(None)
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.deleted_at.is_(None)
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    
    project.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Đã chuyển dự án vào thùng rác thành công!"}

# PHẦN 3: API CHO TASK
@app.post("/projects/{project_id}/tasks/", response_model=task_schema.TaskResponse)
def create_task(project_id: int, task: task_schema.TaskCreate, db: Session = Depends(get_db)):

    project = db.query(project_model.Project).filter(
        project_model.Project.id == project_id,
        project_model.Project.deleted_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại hoặc đã bị xóa")
    
    new_task = task_model.Task(**task.model_dump(exclude={'project_id'}), project_id=project_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/projects/{project_id}/tasks/", response_model=List[task_schema.TaskResponse])
def get_tasks(
    project_id: int, 
    status: Optional[task_schema.TaskStatus] = None, 
    label_id: Optional[int] = None,                  
    db: Session = Depends(get_db)
):
    query = db.query(task_model.Task).filter(
    task_model.Task.project_id == project_id,
    task_model.Task.deleted_at.is_(None)
    )
    
    if status:
        query = query.filter(task_model.Task.status == status)
    if label_id:
        query = query.join(task_label_model.TaskLabel).filter(
            task_label_model.TaskLabel.label_id == label_id
        )
    return query.all()


@app.get("/tasks/{task_id}", response_model=task_schema.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(
        task_model.Task.id == task_id,
        task_model.Task.deleted_at.is_(None)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task không tồn tại")
    return task

@app.put("/tasks/{task_id}", response_model=task_schema.TaskResponse)
def update_task(task_id: int, task_update: task_schema.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(
        task_model.Task.id == task_id,
        task_model.Task.deleted_at.is_(None)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task không tồn tại")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(
        task_model.Task.id == task_id,
        task_model.Task.deleted_at.is_(None)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task không tồn tại")
    
    task.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Đã xóa Task thành công!"}




@app.post("/users/{user_id}/labels/", response_model=label_schema.LabelResponse)
def create_label(user_id: int, label: label_schema.LabelCreate, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # Kiểm tra trùng tên label trong cùng user
    existing = db.query(label_model.Label).filter(
        label_model.Label.user_id == user_id,
        label_model.Label.name == label.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Label đã tồn tại")

    new_label = label_model.Label(**label.model_dump(), user_id=user_id)
    db.add(new_label)
    db.commit()
    db.refresh(new_label)
    return new_label


@app.get("/users/{user_id}/labels/", response_model=List[label_schema.LabelResponse])
def get_user_labels(user_id: int, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    labels = db.query(label_model.Label).filter(
        label_model.Label.user_id == user_id
    ).all()
    return labels


@app.get("/labels/{label_id}", response_model=label_schema.LabelResponse)
def get_label(label_id: int, db: Session = Depends(get_db)):
    label = db.query(label_model.Label).filter(
        label_model.Label.id == label_id
    ).first()

    if not label:
        raise HTTPException(status_code=404, detail="Label không tồn tại")
    return label


@app.put("/labels/{label_id}", response_model=label_schema.LabelResponse)
def update_label(label_id: int, label_update: label_schema.LabelUpdate, db: Session = Depends(get_db)):
    label = db.query(label_model.Label).filter(
        label_model.Label.id == label_id
    ).first()

    if not label:
        raise HTTPException(status_code=404, detail="Label không tồn tại")

    update_data = label_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(label, key, value)

    db.commit()
    db.refresh(label)
    return label


@app.delete("/labels/{label_id}")
def delete_label(label_id: int, db: Session = Depends(get_db)):
    label = db.query(label_model.Label).filter(
        label_model.Label.id == label_id
    ).first()

    if not label:
        raise HTTPException(status_code=404, detail="Label không tồn tại")

    db.delete(label)
    db.commit()
    return {"message": "Đã xóa Label thành công!"}




@app.post("/tasks/{task_id}/labels/{label_id}")
def assign_label_to_task(task_id: int, label_id: int, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(
        task_model.Task.id == task_id,
        task_model.Task.deleted_at.is_(None)
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task không tồn tại")

    label = db.query(label_model.Label).filter(label_model.Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label không tồn tại")

    # Kiểm tra xem đã gán chưa
    existing = db.query(task_label_model.TaskLabel).filter(
        task_label_model.TaskLabel.task_id == task_id,
        task_label_model.TaskLabel.label_id == label_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Label đã được gán cho task này")

    task_label = task_label_model.TaskLabel(task_id=task_id, label_id=label_id)
    db.add(task_label)
    db.commit()
    return {"message": "Đã gán Label vào Task thành công!"}


@app.delete("/tasks/{task_id}/labels/{label_id}")
def remove_label_from_task(task_id: int, label_id: int, db: Session = Depends(get_db)):
    task_label = db.query(task_label_model.TaskLabel).filter(
        task_label_model.TaskLabel.task_id == task_id,
        task_label_model.TaskLabel.label_id == label_id
    ).first()

    if not task_label:
        raise HTTPException(status_code=404, detail="Label chưa được gán cho task này")

    db.delete(task_label)
    db.commit()
    return {"message": "Đã gỡ Label khỏi Task thành công!"}