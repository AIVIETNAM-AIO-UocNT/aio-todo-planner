from database import Base, engine

# Import tất cả model
from models.user import User
from models.project import Project
from models.task import Task
from models.label import Label
from models.task_label import TaskLabel

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()