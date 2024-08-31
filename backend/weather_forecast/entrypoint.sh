#!sh

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "Running in production mode"
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
elif [ "$ENVIRONMENT" = "local" ]; then
    echo "Running in development mode"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "ENVIRONMENT variable is not set"
fi