from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sys
import math
from datetime import datetime
import json
import calendar
from invoices import Invoices
from database.dbmanager import DbManager
from database.tables import Payments
from gDrive import GDrive
import re


app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'
app.debug=True

def calc(expresion):
    
    # Buscar todos los números en la expresión
    numeros = re.findall(r'\d+', expresion)
    
    # Convertir a enteros y sumar
    total = sum(int(num) for num in numeros)
    return total

def get_menu():
    db = DbManager()
    companies = db.get_companies()
    return companies
    #return json.dumps(companies)
    # with open('data.json') as json_file:
    #     data = json.load(json_file)
    # return data

def get_months():
    months = []
    for i in range(1,13):
        months.append(calendar.month_name[i])
    
    return months

def _get_moth_name(number):
    months = get_months()
    return months[number-1]

@app.template_filter()
def format_number(value):
    return '{:,.0f}'.format(value)

@app.route('/')
def index():
    return render_template('index.html', data=get_menu(), months=get_months())

@app.route('/payments', methods=['GET','POST'])
def payments():
    db = DbManager()
    if request.method == 'GET':
        return render_template('summary.html', data=get_menu(), payments=[], id=0)
    else:
        total=0
        id = request.form["id"]
        payments = None
        if id:
            
            payments = db.get_payments(id)
            for p in payments:
                total+=p["value"]
        else:
            id = 0

        return render_template('summary.html', data=get_menu(), payments=payments, id=int(id), total=total)

@app.route('/revoke', methods=['GET'])
def revoke():
    db = DbManager()
    db.delete_parameter('gdrive_token')
    return render_template('index.html', data=get_menu(), months=get_months())


@app.route('/upload', methods=['POST'])
def upload_file():
    db = DbManager()
    invoice = Invoices()
    if  request.form['debtdate'] and request.form['value'] and request.form['category']:
        category = request.form['category'] 
        debdate = request.form['debtdate']
        value = request.form['value']
        notes = request.form['notes']
        children = None
        image = None
        company_id = None
        debdate_date = datetime.strptime(debdate,'%Y-%m-%d')
        month = debdate_date.month
        images = None
        if request.form['imageData']:
            image_data = request.form.get('imageData')
            images = json.loads(image_data) if image_data else []
            
    
        if 'children' in request.form:
            children_id = request.form['children']
            company_id = children_id
            sub_company = db.get_companyByParentId(children_id)
            children = sub_company.name
        else:
            company_id=category
        
        if '+' in value:
            value = calc(value)
            
        company = db.get_companyByParentId(category)
        category = company.name
        files = []
        if images:
            for image_base64 in images:
                # header, base64_data = image_base64.split(',', 1)
                uploaded_file = invoice.upload(category, children,_get_moth_name(month), None, image_base64)
                files.append(uploaded_file[0])

        for file in request.files.getlist('files[]'):
            if file.filename:
                uploaded_file = invoice.upload(category, children,_get_moth_name(month), file, None)
                files.append(uploaded_file[0])
                
        file_names = ','.join([item['filename'] for item in files]) 
        payment = Payments()
        payment.company_id = company_id
        payment.value = value
        payment.debdate = debdate_date
        payment.paymentdate = datetime.today()
        payment.path = file_names
        payment.linkfile = ','.join([item['filelink'] for item in files])
        payment.notes = notes
        pay = db.add_payment(payment)
        return render_template('index.html', message='<br/>'.join([item['filename'] for item in files]) , data=get_menu(), months=get_months())
        
    else:
        return render_template('index.html', message='You need select all felds', data=get_menu())

@app.route('/summary')
def summary():
    db = DbManager()
    total = 0
    items = []
    summary = db.get_summary(26)
    for item in summary:
        total += item.Payments.value
        items.append({"id":item.Payments.id, "value":item.Payments.value, "date":item.Payments.paymentdate, "name":item.name})
    return render_template('payments.html', items=items, total=total)

@app.route('/get_children/<parent_id>', methods=['GET'])
def get_children(parent_id:int):
    db = DbManager()
    sub_companies = db.get_companies(parent_id)
    return json.dumps(sub_companies)
    
    

@app.route('/get_files/<int:parent_id>', methods=['GET'])
def get_files(parent_id):
    db = DbManager()
    invoice = Invoices()
    company = db.get_companyByParentId(parent_id)
    files = invoice.get_files(company.name)
    return jsonify(files)

def main():
    app.run(host="0.0.0.0")


if __name__ == '__main__':
        if len(sys.argv)<=1:
            app.run(host='0.0.0.0')
        else:
            drive = GDrive()
            drive.login()

