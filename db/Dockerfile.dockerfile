FROM python:3.8

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# initialize database 
CMD ["python", "./init_db.py"]