--liquibase formatted sql
--changeset datawookie:8d8d70c226fa

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 8d8d70c226fa

INSERT INTO alembic_version (version_num) VALUES ('8d8d70c226fa');
