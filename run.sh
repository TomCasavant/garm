#!/bin/bash
source .venv/bin/activate
source .env

echo "Flushing Redis database..."
redis-cli FLUSHALL

echo "Starting Redis server..."
redis-server &

sleep 3

echo "Starting Celery worker..."
celery -A make_celery worker --loglevel INFO &

echo "Starting Celery beat..."
celery -A make_celery beat --loglevel DEBUG &

#echo "Starting Flower..."
#celery -A make_celery flower --port=5555 &

echo "All services started!"

# Use Gunicorn to serve the Flask application
gunicorn -w 4 -b 0.0.0.0:8000 "ugs:create_app()" --log-level debug
