web: gunicorn app:wsgi_app --workers=3 --bind 0.0.0.0:$PORT
web_dev: python app.py $PORT
worker: python stream.py