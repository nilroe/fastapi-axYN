from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import  schemas
from clase import models
from config import utils
from config.db import SessionLocal, engine


schemas.Base.metadata.create_all(bind=engine)

crud=APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## GET ##

@crud.get("/users/all", response_model=list[models.UserBase], tags=["USERS"])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.User).offset(skip).limit(limit).all()

@crud.get("/users/{user_id}", response_model=models.UserBase, tags=["USERS"])
def get_user(user_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.User).filter(schemas.User.id == user_id).first()

@crud.get("/users/email/{email}", response_model=models.UserBase, tags=["USERS"])
def get_user_by_email(email:str, db: Session = Depends(get_db)):
    return db.query(schemas.User).filter(schemas.User.email == email).first()

@crud.get("/companies/all", response_model=list[models.CompanyBase], tags=["COMPANIES"])
def get_companys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.Company).offset(skip).limit(limit).all()

@crud.get("/companies/{company_id}", tags=["COMPANIES"])
def get_company(company_id:int, db: Session = Depends(get_db)):
    q = db.query(schemas.Company).filter(schemas.Company.id == company_id).first()
    return  q

@crud.get("/companies/name/{name}", tags=["COMPANIES"])
def company_by_name(name: str, db: Session = Depends(get_db)):
    if name:
        return db.query(schemas.Company).filter(or_(schemas.Company.fiscal_name.contains(name), \
                                            schemas.Company.commercial_name.contains(name))\
                                                ).all()

@crud.get("/movements/all", response_model=list[models.MovementBase], tags=["MOVEMENTS"])
def get_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.Movement).offset(skip).limit(limit).all()

@crud.get("/movements/{movement_id}", response_model=models.MovementBase, tags=["MOVEMENTS"])
def get_movement(movement_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Movement).filter(schemas.Movement.id == movement_id).first()

@crud.get("/signs/all", response_model=list[models.SignBase], tags=["SIGNS"])
def get_signs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.Sign).offset(skip).limit(limit).all()

@crud.get("/signs/{sign_id}", response_model=models.SignBase, tags=["SIGNS"])
def get_sign(sign_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign).filter(schemas.Sign.id == sign_id).first()

@crud.get("/signs/email/{email}", response_model=models.SignBase, tags=["SIGNS"])
def get_signs_by_email(email:str, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(schemas.Sign.user == schemas.User.id \
                & schemas.User.email==email)

@crud.get("/signs/company/{company_id}", response_model=models.SignBase, tags=["SIGNS"])
def get_signs_by_company(company_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(company_id == schemas.User.company \
                & schemas.Sign.user == schemas.User.id)

@crud.get("/signs/user/{user_id}", response_model=models.SignBase, tags=["SIGNS"])
def get_signs_by_company(user_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(schemas.Sign.user == user_id)

## POST ##

@crud.post("/users/post", tags=["USERS"])
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    q=db.query(schemas.User).filter(or_(schemas.User.email==user.email, schemas.User.phone==user.phone)).first()
    if q:
        raise HTTPException(status_code=400, detail="An user already exists with this mail or phone")
    else:
        pwd = utils.crypt_pass(user.password)
        db_user = schemas.User(email=user.email, \
                            hashed_password=pwd, \
                            name=user.name, \
                            phone=user.phone,            
                            company_id=user.company, \
                            is_active=user.active,            
                            is_admin=user.admin, \
                            is_super=user.super, \
                            create_time=user.created,\
                            update_time=user.updated)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

@crud.post("/companies/post", tags=["COMPANIES"])
def create_company(company: models.CompanyCreate, db: Session = Depends(get_db)):
    q=db.query(schemas.Company).filter(schemas.Company.vatnumber==company.vat).first()
    if q:
        raise HTTPException(status_code=400, detail="A company already exists with this vat")
    else:
        db_company = schemas.Company(commercial_name=company.commercial, \
                                 fiscal_name=company.fiscal, \
                                 vatnumber=company.vat, \
                                 is_active=company.active, \
                                 create_time=company.created, \
                                 update_time=company.updated,
                                 )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@crud.post("/movements/post", tags=["MOVEMENTS"])
def create_movement(movement: models.MovementCreate, db: Session = Depends(get_db)):
    q=db.query(schemas.Movement).filter(schemas.Movement.code==movement.code).first()
    if q:
        raise HTTPException(status_code=400, detail="A movement already exists with this code")
    else:
        db_movement = schemas.Movement(code=movement.code, \
                                 description=movement.description, \
                                 is_active=movement.active, \
                                 create_time=movement.created, \
                                 update_time=movement.updated,
                                 )
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return db_movement

@crud.post("/signs/post", tags=["SIGNS"])
def create_user_sign(sign: models.SignCreate, user_id:int, movement_id:int, db: Session = Depends(get_db)):
    db_sign = schemas.Sign(user=user_id, \
                           movement=movement_id, \
                           login = sign.login, \
                           location = sign.location, \
                           identifier = sign.identifier, \
                           create_time=sign.created, \
                           update_time=sign.updated)
    db.add(db_sign)
    db.commit()
    db.refresh(db_sign)
    return db_sign