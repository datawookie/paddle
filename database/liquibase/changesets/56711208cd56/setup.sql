-- Running upgrade e3e94e9034a1 -> 56711208cd56

CREATE TABLE membership_body (
    id INTEGER NOT NULL,
    name VARCHAR,
    acronym VARCHAR,
    PRIMARY KEY (id)
);

ALTER TABLE paddler ADD COLUMN membership_body_id INTEGER;

ALTER TABLE paddler RENAME bcu TO membership_number;

ALTER TABLE paddler RENAME bcu_expiry TO membership_expiry;

UPDATE alembic_version SET version_num='56711208cd56' WHERE alembic_version.version_num = 'e3e94e9034a1';
