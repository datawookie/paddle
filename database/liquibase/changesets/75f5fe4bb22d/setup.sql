-- Running upgrade 68cf0f59baf7 -> 75f5fe4bb22d

ALTER TABLE crew DROP COLUMN team_id;

UPDATE alembic_version SET version_num='75f5fe4bb22d' WHERE alembic_version.version_num = '68cf0f59baf7';
