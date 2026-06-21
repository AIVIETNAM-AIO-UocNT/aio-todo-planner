from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/to_do_list"

engine = create_engine(DATABASE_URL)

Base = declarative_base()