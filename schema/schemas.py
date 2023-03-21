from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship

from config.db import Base


# TABLAS #
class SimpleUsers(Base):
    __tablename__ = "simpleusers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)

    SimpleLogs = relationship('SimpleLogs', back_populates='User')

class SimpleLogs(Base):
    __tablename__ = "simplelogs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('simpleusers.id'), nullable=False)
    loginTime = Column(DateTime, default=datetime.utcnow)
    action = Column(String(50), index=True)
    proof = Column(String(2500))
    longitude =Column(String(50))
    latitude = Column(String(50))

    User = relationship('SimpleUsers', back_populates='SimpleLogs')

class SimplePass(Base):
    __tablename__ = "simplepass"
       
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(250)) 

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    commercial_name = Column(String(250), index=True, nullable=False)
    fiscal_name = Column(String(250), index=True, nullable=False)
    vatnumber = Column(String(50), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)

    User = relationship("User", back_populates="Company")
   
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    email = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100))
    phone = Column(String(50),nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_super = Column(Boolean, default=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)

    Company = relationship('Company', back_populates='User')
    Sign = relationship('Sign', back_populates='User')

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), index=True, unique=True)
    description = Column(String(250), index=True)
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)

    Sign = relationship("Sign", back_populates="Movement")


class Sign(Base):
    __tablename__ = "signs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    login = Column(DateTime, nullable=False)
    movement = Column(Integer, ForeignKey('movements.id'), nullable=False)
    location = Column(String(250))
    identifier = Column(String(250))
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow)

    User = relationship('User', back_populates='Sign')
    Movement = relationship('Movement', back_populates='Sign')