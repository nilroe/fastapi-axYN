from sqlalchemy import create_engine, URL   
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

url_object = URL.create(
    "mysql+pymysql",
    username="loginapp",
    password="repr0gest",
    host="localhost",
    database="loginapp",
)

engine = create_engine(url_object)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()