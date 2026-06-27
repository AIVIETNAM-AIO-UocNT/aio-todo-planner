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
    task_label as task_label_model
)

from schemas import (
    user as user_schema, 
    project as project_schema, 
    task as task_schema
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