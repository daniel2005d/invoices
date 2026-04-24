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
        today = date.today()
    
        # Determinamos el inicio del ciclo
        if today.day >= 26:
            # Caso: 26 al 31 de este mes
            # El ciclo empieza el 26 de este mes y termina el 25 del próximo
            start_date = datetime(today.year, today.month, 26)
            
            # Manejo del próximo mes y posible cambio de año
            if today.month == 12:
                end_date = datetime(today.year + 1, 1, 25)
            else:
                end_date = datetime(today.year, today.month + 1, 25)
        else:
            # Caso: 1 al 25 de este mes
            # El ciclo empezó el 26 del mes anterior y termina el 25 de este mes
            end_date = datetime(today.year, today.month, 25)
            
            # Manejo del mes anterior y posible cambio de año
            if today.month == 1:
                start_date = datetime(today.year - 1, 12, 26)
            else:
                start_date = datetime(today.year, today.month - 1, 26)
    
            # La consulta usando los límites correctos
        query = session.query(Payments, Company.name)\
            .join(Company, Company.id == Payments.company_id)\
            .where(Payments.debdate.between(start_date, end_date))
        #query = session.query(Payments, Company.name).join(Company, Company.id==Payments.company_id).where(Payments.debdate.between(cleft,cright))
        print(query)
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









    