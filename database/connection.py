from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:3A9eQAHluSe7@10.0.0.253:5432/invoice', 
                       connect_args={'connect_timeout':10, 'application_name':'invoices'}, pool_size=20, max_overflow=0)

Session = sessionmaker(bind=engine)
session = Session()

