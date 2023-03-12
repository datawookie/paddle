-- Running upgrade 915a89d96e8b -> e3e94e9034a1

ALTER TABLE race ADD COLUMN time_adjustment INTEGER;

UPDATE alembic_version SET version_num='e3e94e9034a1' WHERE alembic_version.version_num = '915a89d96e8b';
