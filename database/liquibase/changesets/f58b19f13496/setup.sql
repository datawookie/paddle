--liquibase formatted sql
--changeset datawookie:f58b19f13496
--precondition-sql-check expectedResult:1 SELECT COUNT(*) FROM alembic_version WHERE version_num = '4f370a25634c'
--comment Running upgrade 4f370a25634c -> f58b19f13496

ALTER TABLE club ADD COLUMN services BOOLEAN DEFAULT 0;

UPDATE alembic_version SET version_num='f58b19f13496' WHERE alembic_version.version_num = '4f370a25634c';
