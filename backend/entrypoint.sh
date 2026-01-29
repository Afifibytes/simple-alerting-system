#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h db -U postgres -q; do
    sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Run seeder if SEED_DATABASE is set
if [ "${SEED_DATABASE:-false}" = "true" ]; then
    echo "Seeding database..."
    python seeder.py
fi

# Execute the main command
exec "$@"
