from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import User
from passlib.context import CryptContext
from routers import dashboard_router, labels_router, projects_router, tasks_router
from schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(
    title="To-Do List Planner API",
    description="Backend API for the AIO Conquer 2026 task management application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(labels_router)
app.include_router(dashboard_router)


@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    - Email must be valid (validated by Pydantic EmailStr)
    - Password is bcrypt-hashed before storage
    - Username and email must be unique
    """
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already in use.")

    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already in use.")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=pwd_context.hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@app.get("/health", tags=["System"])
def health():
    """Returns 200 if the server is running."""
    return {"status": "ok"}
