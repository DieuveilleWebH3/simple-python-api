
// web: python manage.py runserver 0.0.0.0:5000

// web: gunicorn simple_python_api.wsgi:application --log-file - --log-level debug

web: gunicorn simple_python_api.wsgi:application --log-file -

// python manage.py collectstatic --noinput

manage.py migrate
