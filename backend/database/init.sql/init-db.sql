-- Script d'initialisation de la base de données
-- Traffic Simulation Platform

-- Créer la base de données de test
CREATE DATABASE traffic_test;

-- Créer l'utilisateur si il n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'traffic_user') THEN
        CREATE USER traffic_user WITH PASSWORD 'traffic_pass';
    END IF;
END
$$;

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE traffic_db TO traffic_user;
GRANT ALL PRIVILEGES ON DATABASE traffic_test TO traffic_user;

-- Se connecter à la base de données principale
\c traffic_db;

-- Accorder les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO traffic_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO traffic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO traffic_user;

-- Configurer les privilèges par défaut
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO traffic_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO traffic_user;

-- Se connecter à la base de données de test
\c traffic_test;

-- Accorder les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO traffic_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO traffic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO traffic_user;

-- Configurer les privilèges par défaut
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO traffic_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO traffic_user;

-- Message de confirmation
\echo 'Base de données initialisée avec succès!'
