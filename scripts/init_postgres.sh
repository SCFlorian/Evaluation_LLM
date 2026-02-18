#!/bin/bash

echo "Initialisation de la base PostgreSQL..."

psql postgres <<EOF
CREATE DATABASE sportsee_nba_stats;
CREATE USER sportsee_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE sportsee_nba_stats TO sportsee_user;
ALTER DATABASE sportsee_nba_stats OWNER TO sportsee_user;
EOF

echo "Base de données créée avec succès."