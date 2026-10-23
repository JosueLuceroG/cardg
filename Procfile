release: python manage.py migrate
web: gunicorn icard.wsgi:application --bind 0.0.0.0:$PORT --log-file -
