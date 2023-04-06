from . import schemas
import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy import or_, and_, text, case, update
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

@crud.get('/getusers/active', tags=["SIMPLE"])
def get_users(db: Session = Depends(get_db)):
    y = text("select s.name from simpleusers s where is_active=1")
    return db.execute(y).mappings().all()
    #return db.query(schemas.SimpleUsers).where(schemas.SimpleUsers.is_active==1).all()

@crud.get('/getusers/inactive', tags=["SIMPLE"])
def get_users(db: Session = Depends(get_db)):
    y = text("select s.name from simpleusers s where is_active=0")
    return db.execute(y).mappings().all()
    #return db.query(schemas.SimpleUsers).where(schemas.SimpleUsers.is_active==0).all()

@crud.get('/getuserswithlastmove', tags=["SIMPLE"])
def get_users(db: Session = Depends(get_db)):
    y = text("SELECT s.id, s.name, ifnull((SELECT l.action FROM simplelogs l WHERE l.user=s.id and action <> :z ORDER BY l.id DESC LIMIT 1), :q) AS move, (SELECT l.loginTime FROM simplelogs l WHERE l.user=s.id and action <> :z ORDER BY l.id DESC LIMIT 1) as LoginTime FROM simpleusers s where is_active=1")
    args = {"q": "SALIDA", "z":"COMM"}
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
    y = text("SELECT s.id, s.name, ifnull((SELECT l.ACTION FROM simplelogs l WHERE l.user=s.id ORDER BY l.id DESC LIMIT 1), :q) AS move FROM simpleusers s where s.name = :z")
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

@crud.get('/dashboard/all', tags=["DASHBOARD"])
def get_dashboard_all(db: Session = Depends(get_db)):
    y = text("SELECT s.name AS usuario \
		,IFNULL( \
		(CASE WHEN WEEKDAY(NOW())=1  \
			THEN \
			(SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)-3)  \
			ELSE \
			(SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)-1) \
			END) \
		,'N/A')  \
		AS 'DIA_ANTERIOR'  \
		,IFNULL((SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND semana = WEEK(NOW()) AND anyo=YEAR(NOW())),'N/A') AS 'SEMANA_ACTUAL'  \
		,IFNULL((SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND semana = WEEK(NOW())-1 AND anyo=YEAR(NOW())),'N/A') AS 'SEMANA_ANTERIOR'  \
		,IFNULL((SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND mes = MONTH(NOW()) AND anyo=YEAR(NOW())),'N/A') AS 'MES_ACTUAL'  \
		,IFNULL((SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND mes = MONTH(NOW())-1 AND anyo=YEAR(NOW())),'N/A') AS 'MES_ANTERIOR ' \
        FROM simpleusers s  where is_active=1 \
        GROUP BY s.name")  
    result = db.execute(y)
    r = result.mappings().all()
    return r

@crud.get('/dashboard/{usu}/{datefrom}/{dateto}', tags=["DASHBOARD"])
def get_user_dash(usu:str, datefrom:str, dateto:str, db: Session = Depends(get_db)):
    y = text("SELECT u.name AS usuario, \
                    IFNULL((SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') FROM shift_statistics s WHERE s.usuario=u.name AND fecha BETWEEN :df AND :dt) \
                        ,'N/A') AS horas \
             FROM simpleusers u \
             WHERE u.name = :q \
             GROUP BY u.name")
    args = {'q':usu, 'df':datefrom, 'dt':dateto}
    result = db.execute(y, args)     
    r = result.mappings().all()
    return r

## POST ##
@crud.post("/changepass/{tkn}/{nwtkn}", tags=["SIMPLE"])
def change_pass(tkn: str, nwtkn:str, db: Session = Depends(get_db)):
    pwd = utils.crypt(tkn)
    npwd = utils.crypt(nwtkn)
    usu = db.query(schemas.SimplePass).filter(schemas.SimplePass.token == pwd)
    if usu.count() == 1:
        usu.update({'token': npwd})
        db.commit()
        return {"status": "Password Changed"}
    else:
            return {"status": "Error in Password"}
    
@crud.post("/disable/{userapi}", tags=["SIMPLE"])
def disable_user(userapi: str, db: Session = Depends(get_db)):
    usu = db.query(schemas.SimpleUsers).filter(schemas.SimpleUsers.name == userapi)
    if usu.count() >= 1:
        usu.update({'is_active': 0})
        db.commit()
        return {"status": "User Disabled"}
    else:
            return {"status": "Error in Disable"}
    
@crud.post("/enable/{userapi}", tags=["SIMPLE"])
def enable_user(userapi: str, db: Session = Depends(get_db)):
    usu = db.query(schemas.SimpleUsers).filter(schemas.SimpleUsers.name == userapi)
    if usu.count() >= 1:
        usu.update({'is_active': 1})
        db.commit()
        return {"status": "User Enabled"}
    else:
            return {"status": "Error in Enable"}

@crud.post("/user", tags=["SIMPLE"])
def create_user(user: models.SimpleUser, db: Session = Depends(get_db)):
    db_user = schemas.SimpleUsers(name = user.name, is_active = user.isActive, create_time = user.created, update_time = user.updated)
    db.add(db_user)
    db.commit()           
    db.refresh(db_user)           
    return db_user

@crud.post("/logs", tags=["SIMPLE"])
def create_log(log: models.SimpleLogCreate, db: Session = Depends(get_db)):
    db_log = schemas.SimpleLogs(user = log.user, action = log.action, comment= log.comment, loginTime = log.login, longitude=log.longitude, latitude=log.latitude, proof=log.proof)
    db.add(db_log)
    db.commit()           
    db.refresh(db_log)           
    return db_log