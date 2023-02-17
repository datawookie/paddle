--liquibase formatted sql
--changeset datawookie:c110e697b81a
--precondition-sql-check expectedResult:1 SELECT COUNT(*) FROM alembic_version WHERE version_num = 'a82fa9a9e38b'

-- Running upgrade a82fa9a9e38b -> c110e697b81a

INSERT INTO team_type (label) VALUES ('Junior');
--rollback DELETE FROM team_type WHERE label = 'Junior';

INSERT INTO team_type (label) VALUES ('Senior');
--rollback DELETE FROM team_type WHERE label = 'Senior';

UPDATE alembic_version SET version_num='c110e697b81a' WHERE alembic_version.version_num = 'a82fa9a9e38b';
