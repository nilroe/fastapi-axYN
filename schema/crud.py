from . import schemas
from datetime import datetime
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

@crud.get('/logs/nextid', tags=["SIMPLE"])
def get_last_id(db: Session = Depends(get_db)):
    y = text("select max(id)+1 as id from simplelogs")
    resp = db.execute(y)
    r = resp.mappings().all()
    return r

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
    y = text("Select y.name, l.* from simplelogs l left join simpleusers y on l.user=y.id where cast(l.logintime as date) between cast(:df as date) and cast(:dt as date) order by l.id desc")
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
		,IFNULL((select action from simplelogs y WHERE y.user=s.id order by id desc LIMIT 1),'N/A') AS 'ULTIMO_MOVIMIENTO' \
		,IFNULL( \
			if( \
				(select action from simplelogs y WHERE y.user=s.id order by id desc LIMIT 1)='ENTRADA' \
					,(SELECT CONCAT((FLOOR(SUM(minutos)/60)+(SELECT floor(time_to_sec(TIMEDIFF(NOW(),logintime))/60/60) FROM simplelogs x WHERE x.USER=s.id ORDER BY x.id DESC LIMIT 1)),'h ' \
						,MOD(SUM(minutos+(SELECT floor(time_to_sec(TIMEDIFF(NOW(),logintime))/60)FROM simplelogs x WHERE x.USER=s.id ORDER BY x.id DESC LIMIT 1)),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)) \
					,(SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)) \
					) \
			,'N/A') AS 'HOY' \
		,IFNULL( \
		(CASE WHEN WEEKDAY(NOW())=1  \
			THEN  \
			(SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)-3)  \
			ELSE \
			(SELECT CONCAT(FLOOR(SUM(minutos)/60),'h ',MOD(SUM(minutos),60),'m') AS Shift FROM shift_statistics z WHERE z.usuario=s.name AND fecha = cast(NOW() AS DATE)-1)  \
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
    y = text("CALL getcurrentwork(:q, :df, :dt)")
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
            return {"status": "Error Enabling User"}

@crud.post("/user/{usr}", tags=["SIMPLE"])
def create_user(usr: str, db: Session = Depends(get_db)):
    y = text('select s.name from simpleusers s where s. name=:q')
    args = {'q':usr}
    result = db.execute(y, args)     
    r = result.mappings().all()
    if(r):
            return {"status": "ERROR - User already exists"}
    else:
        now = datetime.today()
        db_user = schemas.SimpleUsers(name = usr, is_active = True, create_time = now, update_time = now)
        db.add(db_user)
        db.commit()           
        db.refresh(db_user)           
        return db_user

@crud.post("/logs", tags=["SIMPLE"])
def create_log(log: models.SimpleLogCreate, db: Session = Depends(get_db)):
    y = text('select loginTime from simplelogs where user=:q and logintime BETWEEN :t-INTERVAL 90 SECOND AND :t+INTERVAL 1 minute and action=:a')
    args = {'q':log.user, 't':log.login, 'a':log.action}
    res = db.execute(y,args)
    r = res.mappings().all()

    if r:
        return {"status": "duplicate entry"}
    else:
        m = text('select action from simplelogs where user=:q order by id desc limit 1')
        margs ={'q':log.user}
        mres = db.execute(m, margs)
        mr = mres.fetchone()
        if mr:
            if mr[0] == log.action:
                return {"status": "invalid entry"}
            else:
                comm = utils.removeacccents(log.comment)
                db_log = schemas.SimpleLogs(user = log.user, action = log.action, comment= comm, loginTime = log.login, longitude=log.longitude, latitude=log.latitude, proof=log.proof)
                db.add(db_log)
                db.commit()           
                db.refresh(db_log)           
                return db_log
        else:
                comm = utils.removeacccents(log.comment)
                db_log = schemas.SimpleLogs(user = log.user, action = log.action, comment= comm, loginTime = log.login, longitude=log.longitude, latitude=log.latitude, proof=log.proof)
                db.add(db_log)
                db.commit()           
                db.refresh(db_log)           
                return db_log

@crud.post("/logs/addnewempty", tags=["SIMPLE"])
def create_empty_log(db: Session = Depends(get_db)):
  now = datetime.today()
  db.add(schemas.SimpleLogs(loginTime = now))
  db.commit()
  return db.query(schemas.SimpleLogs).order_by(schemas.SimpleLogs.id.desc()).first()

@crud.delete("/logs/delete/{logid}", tags=["SIMPLE"])
def delete_log(log: int, db: Session = Depends(get_db)):
    db.query(schemas.SimpleLogs).filter(schemas.SimpleLogs.id == log).delete() 
    db.commit() 
    return {"status": "Log Deleted"} 

@crud.put("/logs/update", tags=["SIMPLE"])
def update_log( log: models.SimpleLogCreate, db: Session = Depends(get_db)):
    db_log = db.query(schemas.SimpleLogs).filter(schemas.SimpleLogs.id == log.id).first() 
    if db_log: 
        stm = update(schemas.SimpleLogs).where(schemas.SimpleLogs.id==log.id).values(user = log.user, action = log.action, comment= log.comment, loginTime = log.login)
        db.execute(stm)
        db.commit() 
        return db_log 
    else: 
        return {"status": "ERROR - Log not found"}
    



## GET FOODS ##

@crud.get('/food/getAll', tags=["FOODS"])
def get_foods(db: Session = Depends(get_db)):
    return db.query(schemas.Food).all()    