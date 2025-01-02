source .venv/bin/activate
source .env

echo "Flushing Redis database..."
redis-cli FLUSHALL

echo "Starting Redis server..."
redis-server &

sleep 3

echo "Starting Celery worker..."
gnome-terminal -- bash -c "celery -A make_celery worker --loglevel INFO; exec bash"

echo "Starting Celery beat..."
gnome-terminal -- bash -c "celery -A make_celery beat --loglevel DEBUG; exec bash"

echo "Starting Flower..."
gnome-terminal -- bash -c "celery -A make_celery flower --port=5555; exec bash"

echo "All services started!"

flask --app ugs run --debug