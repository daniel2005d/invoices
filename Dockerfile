FROM python:3.11-slim
WORKDIR /var/www/invoices
COPY . /var/www/invoices
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#CMD ["python" "/var/www/invoices/app.py"]
CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "9001"]
