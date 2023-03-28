from . import schemas
import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy import or_, and_, text, case
from sqlalchemy.orm import Session
from clase import models
from config import utils, handler
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

@crud.get('/getusers', tags=["SIMPLE"])
def get_users(db: Session = Depends(get_db)):
    return db.query(schemas.SimpleUsers).all()

@crud.get('/getuserswithlastmove', tags=["SIMPLE"])
def get_users(db: Session = Depends(get_db)):
    y = text("SELECT s.id, s.NAME, ifnull((SELECT l.ACTION FROM simplelogs l WHERE l.user=s.id ORDER BY l.id DESC LIMIT 1), :q) AS move FROM simpleusers s")
    args = {"q": "SALIDA"}
    res= db.execute(y, args)
    r = res.mappings().all()
    return r

@crud.get('/getuserbyname/{username}', tags=["SIMPLE"])
def get_users(username:str, db: Session = Depends(get_db)):
    return db.query(schemas.SimpleUsers).filter(schemas.SimpleUsers.name == username).all()

@crud.get('/getuser/{userid}', tags=["SIMPLE"])
def get_users(userid:int, db: Session = Depends(get_db)):
    return db.query(schemas.SimpleUsers).filter(schemas.SimpleUsers.id == userid).first()

@crud.get('/getlogs', tags=["SIMPLE"])
def get_logs(db: Session = Depends(get_db)):
    return db.query(schemas.SimpleLogs).all()

@crud.get('/getlogs/{userapi}', tags=["SIMPLE"])
def get_logs(userapi:str, db: Session = Depends(get_db)):
    y = text("SELECT s.id, s.NAME, ifnull((SELECT l.ACTION FROM simplelogs l WHERE l.user=s.id ORDER BY l.id DESC LIMIT 1), :q) AS move FROM simpleusers s where s.name = :z")
    args = {"q": "SALIDA", "z": userapi}
    res= db.execute(y, args)
    r = res.mappings().all()
    return r

@crud.get('/getnextmovementbyuser/{userid}', tags=["SIMPLE"])
def get_users(userid:int, db: Session = Depends(get_db)):
    y = text("select (case when action = :2 then :1 else :2 end) as action from simplelogs where user = :userid order by id desc limit 1")
    args = {'userid': userid, '1': "ENTRADA", '2': "SALIDA"}
    res= db.execute(y, args)
    r = res.mappings().all()
    return r

@crud.get('/getlogs/date/{datefrom}/{dateto}', tags=["SIMPLE"])
def get_logs(datefrom:str, dateto:str, db: Session = Depends(get_db)):
    y = text("Select y.name, l.* from simplelogs l inner join simpleusers y on l.user=y.id where cast(l.logintime as date) between cast(:df as date) and cast(:dt as date) order by l.logintime")
    args = {'df' : datefrom, 'dt': dateto}
    result = db.execute(y, args)     
    r = result.mappings().all()
    return r

@crud.get('/getlogs/dates/{userapi}/{datefrom}/{dateto}', tags=["SIMPLE"])
def get_logs(userapi:str, datefrom:str, dateto:str, db: Session = Depends(get_db)):
    y = text("Select y.name, l.* from simplelogs l inner join simpleusers y on l.user=y.id where cast(l.logintime as date) between cast(:df as date) and cast(:dt as date) and name like :userapi order by l.logintime")
    userapi = "%{}%".format(userapi)
    args = {'df' : datefrom, 'dt': dateto, 'userapi':userapi}
    result = db.execute(y, args)     
    r = result.mappings().all()
    return r

@crud.get('/pass/{token}', tags=["SIMPLE"])
def check_pass(token:str, db: Session = Depends(get_db)):
    pwd = utils.crypt(token)
    return db.query(schemas.SimplePass).filter(schemas.SimplePass.token == pwd).first()

@crud.get("/users/all", tags=["USERS"])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.User).offset(skip).limit(limit).all()

@crud.get("/users/{user_id}", tags=["USERS"])
def get_user(user_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.User).filter(schemas.User.id == user_id).first()

@crud.get("/users/email/{email}", tags=["USERS"])
def get_user_by_email(email:str, db: Session = Depends(get_db)):
    return db.query(schemas.User).filter(schemas.User.email == email).first()

@crud.get("/companies/all", tags=["COMPANIES"])
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

@crud.get("/movements/all", tags=["MOVEMENTS"])
def get_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.Movement).offset(skip).limit(limit).all()

@crud.get("/movements/{movement_id}", tags=["MOVEMENTS"])
def get_movement(movement_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Movement).filter(schemas.Movement.id == movement_id).first()

@crud.get("/signs/all", tags=["SIGNS"])
def get_signs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(schemas.Sign).offset(skip).limit(limit).all()

@crud.get("/signs/{sign_id}", tags=["SIGNS"])
def get_sign(sign_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign).filter(schemas.Sign.id == sign_id).first()

@crud.get("/signs/email/{email}", tags=["SIGNS"])
def get_signs_by_email(email:str, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(and_(schemas.Sign.user == schemas.User.id \
                , schemas.User.email==email))

@crud.get("/signs/company/{company_id}", tags=["SIGNS"])
def get_signs_by_company(company_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(and_(company_id == schemas.User.company \
                , schemas.Sign.user == schemas.User.id))

@crud.get("/signs/user/{user_id}", tags=["SIGNS"])
def get_signs_by_company(user_id:int, db: Session = Depends(get_db)):
    return db.query(schemas.Sign, schemas.User)\
        .filter(schemas.Sign.user == user_id)

@crud.get("/tkn", tags=["LOGIN"])
def de_token(token: str):
    return handler.deToken(token)


## POST ##
@crud.post("/changepass/{token}", tags=["SIMPLE"])
def change_pass(token: str, db: Session = Depends(get_db)):
    pwd = utils.crypt(token)
    db_pwd = schemas.SimplePass(token=pwd)
    db.add(db_pwd)
    db.commit()
    db.refresh(db_pwd)
    return db_pwd

@crud.post("/user", tags=["SIMPLE"])
def create_user(user: models.SimpleUser, db: Session = Depends(get_db)):
    db_user = schemas.SimpleUsers(name = user.name, is_active = user.isActive, create_time = user.created, update_time = user.updated)
    db.add(db_user)
    db.commit()           
    db.refresh(db_user)           
    return db_user

@crud.post("/logs", tags=["SIMPLE"])
def create_log(log: models.SimpleLogCreate, db: Session = Depends(get_db)):
    db_log = schemas.SimpleLogs(user = log.user, action = log.action, loginTime = log.login, longitude=log.longitude, latitude=log.latitude, proof=log.proof)
    db.add(db_log)
    db.commit()           
    db.refresh(db_log)           
    return db_log

@crud.post("/login", tags=["LOGIN"])
def user_login(login: models.Login, db: Session = Depends(get_db)):
    pwd = utils.crypt(login.password)
    log = db.query(schemas.User).filter(and_(schemas.User.email == login.email , schemas.User.hashed_password == pwd)).first()
    if log:
        z= handler.enToken(log.id, log.company_id)
        return z
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@crud.post("/users/post", tags=["USERS"])
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    q=db.query(schemas.User).filter(or_(schemas.User.email==user.email, schemas.User.phone==user.phone)).first()
    if q:
        raise HTTPException(status_code=400, detail="An user already exists with this mail or phone")
    else:
        pwd = utils.crypt(user.password)
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