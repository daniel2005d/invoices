from sqlalchemy import desc
from database.connection import Session
from database.tables import Company, Payments, Parameters
from datetime import date, timedelta, datetime

class DbManager:
    def get_companies(self, parent_id=None):
        companies = []
        session = Session()
        query=None
        if parent_id is None:
            query = session.query(Company).where(Company.parent_id == None).order_by(Company.name)
        else:
            query = session.query(Company).where(Company.parent_id==parent_id).order_by(Company.name)

        result = query.all()
        session.close()
        for c in result:
            companies.append({"id":c.id,"name":c.name,"parent_id":c.parent_id})

        return companies

    def get_companyByParentId(self, parentId:int):
        company = None
        session = Session()
        query = session.query(Company).where(Company.id == parentId)
        company = query.first()
        session.close()
        return company
    
    def add_payment(self, invoice:Payments):
        session = Session()
        session.add(invoice)
        session.commit()
        session.close()
        return invoice
    
    def get_summary(self, day_of_month=20):
        rows = None
        session = Session()
     
            # La consulta usando los límites correctos
        query = session.query(Payments, Company.name)\
            .join(Company, Company.id == Payments.company_id)\
            .order_by(desc(Payments.id)).limit(30)
        
        rows = query.all()
        session.close()
        return rows


    def get_payments(self, id:int):
        if id:
            session = Session()
            company_query = session.query(Company).where(Company.parent_id == id)
            company = company_query.first()
            query = None
            if company:
                query = session.query(Payments, Company).join(Company, Payments.company_id == Company.id).where(Company.parent_id==id).order_by(Payments.debdate.desc())
            else:
                query = session.query(Payments, Company).join(Company, Payments.company_id == Company.id).where(Company.id==id).order_by(Payments.debdate.desc())
            

            payments = []
            
            result = query.all()
            session.close()
            for r in result:
                payments.append({"name":r.Company.name,
                                "value":r.Payments.value, 
                                "debdate":r.Payments.debdate,
                                "paymentdate":r.Payments.paymentdate,
                                "notes":r.Payments.notes,
                                "files":r.Payments.path.split(','),
                                "links": r.Payments.linkfile.split(',') if r.Payments.linkfile else None
                                })
            
            return payments
    
    def get_parameter(self, name:str)->str:
        session = Session()
        query = session.query(Parameters.value).where(Parameters.name == name)
        value = query.first()
        session.close()
        if value:
            return value.value

        return None
    
    def create_parameter(self, name:str, value:str):
        session = Session()
        parameter = Parameters()
        parameter.value = value
        parameter.name = name
        session.add(parameter)
        session.commit()
        session.close()
    
    def delete_parameter(self, name:str):
        session = Session()
        query = session.query(Parameters).filter_by(name=name).first()
        if query:
            session.delete(query)
            session.commit()
        
        session.close()









    