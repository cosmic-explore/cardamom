FROM python:3.8

# set a directory for the app
WORKDIR /usr/src/cardamom

# copy all files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the Flask app will run on
EXPOSE 5000

# start the server
CMD ["python", "./app.py", "--host=0.0.0.0", "--debug"]