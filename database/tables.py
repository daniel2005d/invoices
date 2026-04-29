from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey, UUID, Text, Double
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
class Company(Base):
    __tablename__ = 'company'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_id = Column(Integer)

class Email:
    __tablename__ = 'email'
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    subject = Column(String)
    body = Column(String)
    company_id = Column(Integer)

class Payments(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, nullable=False)
    value = Column(Double, nullable=False)
    debdate = Column(Date, nullable=False)
    paymentdate = Column(Date, nullable=False)
    path = Column(String, nullable=False)
    linkfile = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    method = Column(String, nullable=True)

class Parameters(Base):
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Text, nullable=False)