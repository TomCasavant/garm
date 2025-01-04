#!/bin/bash

echo "Stopping Gunicorn..."
pkill -f gunicorn

echo "Stopping Celery worker..."
pkill -f "celery worker"

echo "Stopping Celery beat..."
pkill -f "celery beat"

# Uncomment if Flower is running
# echo "Stopping Flower..."
# pkill -f "celery flower"

echo "Stopping Redis server..."
pkill -f redis-server

echo "All services stopped!"
