CREATE USER selvbetjening WITH PASSWORD 'selvbetjening' CREATEDB;
CREATE DATABASE selvbetjening
    WITH
    OWNER = selvbetjening
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
