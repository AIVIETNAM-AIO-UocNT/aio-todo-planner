# main.py
from database import Base, engine
from models import User, Project, Task, Label, TaskLabel

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

def main():
    init_db()  
    
    print("\nchạy thành công")
    
if __name__ == "__main__":
    main()