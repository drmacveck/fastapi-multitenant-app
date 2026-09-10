#!/bin/sh
set -e

echo "Waiting for database connection..."
python -c "
import socket, time, os
host = os.getenv('DB_HOST', 'db')
port = int(os.getenv('DB_PORT', 5432))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        time.sleep(0.5)
"

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn Main:app --host 0.0.0.0 --port 8000
