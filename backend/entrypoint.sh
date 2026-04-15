#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python -c "import os, time, psycopg
host = os.getenv('POSTGRES_HOST', 'db')
port = os.getenv('POSTGRES_PORT', '5432')
dbname = os.getenv('POSTGRES_DB', 'vaur')
user = os.getenv('POSTGRES_USER', 'vaur')
password = os.getenv('POSTGRES_PASSWORD', '')

for attempt in range(30):
    try:
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        conn.close()
        break
    except psycopg.OperationalError:
        time.sleep(1)
else:
    raise SystemExit('PostgreSQL is unavailable after 30 seconds')"

python manage.py migrate

exec "$@"
