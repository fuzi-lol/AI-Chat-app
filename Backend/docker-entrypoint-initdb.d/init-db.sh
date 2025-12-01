#!/bin/bash
set -e

# Get database name from environment variable or use default
DB_NAME="${POSTGRES_DB:-chatapp}"
DB_USER="${POSTGRES_USER:-chatapp_user}"

echo "Ensuring database $DB_NAME exists..."

# Connect to postgres database (which always exists) and create the target database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE $DB_NAME'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOSQL

# Grant all privileges to the user on the database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
EOSQL

echo "Database $DB_NAME initialized successfully with user $DB_USER"

