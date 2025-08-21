#!/bin/sh

# seed the database if needed and start the server

echo Running init_db.py
python init_db.py

FLASK_ENV=${FLASK_ENV:-development}

echo starting gunicorn in $FLASK_ENV mode
if [ "$FLASK_ENV" = "development" ]; then
    exec gunicorn -b 0.0.0.0:5000 app:app --workers=4 --reload --worker-class=gevent --timeout=6000 --access-logfile -
else
    # no reloading
    exec gunicorn -b 0.0.0.0:5000 app:app --workers=4 --worker-class=gevent --timeout=6000 --access-logfile -
fi