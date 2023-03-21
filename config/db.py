from sqlalchemy import create_engine, URL   
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

url_object = URL.create(
    "mysql+pymysql",
    username="otwkyrzy_loginapp",
    password="f1anjxwGlNG87n0Xwd",
    host="sc-europe80.banahosting.com",
    database="otwkyrzy_loginapp"
)

engine = create_engine(url_object, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()