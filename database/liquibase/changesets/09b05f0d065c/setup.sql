--liquibase formatted sql
--changeset datawookie:09b05f0d065c
--precondition-sql-check expectedResult:1 SELECT COUNT(*) FROM alembic_version WHERE version_num = '915a89d96e8b'

-- Running upgrade 915a89d96e8b -> 09b05f0d065c

INSERT INTO category (label) VALUES ('K2 Senior');
INSERT INTO category (label) VALUES ('K2 Junior');
INSERT INTO category (label) VALUES ('K2 Ladies');
INSERT INTO category (label) VALUES ('K2 Junior Ladies');
INSERT INTO category (label) VALUES ('K2 Veteran');
INSERT INTO category (label) VALUES ('K2 Mixed');
INSERT INTO category (label) VALUES ('K2 Junior/Veteran');
INSERT INTO category (label) VALUES ('K1 Senior');
INSERT INTO category (label) VALUES ('K1 Junior');
INSERT INTO category (label) VALUES ('K1 Ladies');
INSERT INTO category (label) VALUES ('K1 Veteran');
INSERT INTO category (label) VALUES ('C2');
INSERT INTO category (label) VALUES ('C1');

UPDATE alembic_version SET version_num='09b05f0d065c' WHERE alembic_version.version_num = '915a89d96e8b';
