--liquibase formatted sql
--changeset datawookie:4f370a25634c

-- Running upgrade c110e697b81a -> 4f370a25634c

INSERT INTO age_group (id, label) VALUES (1, 'Junior');
INSERT INTO age_group (id, label) VALUES (2, 'Senior');
INSERT INTO age_group (id, label) VALUES (3, 'Veteran');
INSERT INTO age_group (id, label) VALUES (4, 'Master');

UPDATE alembic_version SET version_num='4f370a25634c' WHERE alembic_version.version_num = 'c110e697b81a';
