CREATE SCHEMA IF NOT EXISTS football;

SET search_path TO football;

CREATE TABLE IF NOT EXISTS countries(
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(30) UNIQUE NOT NULL
);
