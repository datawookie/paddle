-- Running upgrade c8cd8ff9c99e -> 0dc044ac3c23

CREATE TABLE race_number (
    id INTEGER NOT NULL,
    race_id INTEGER,
    category_id INTEGER,
    min_number_id INTEGER,
    max_number_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(category_id) REFERENCES category (id),
    FOREIGN KEY(min_number_id) REFERENCES number (id),
    FOREIGN KEY(max_number_id) REFERENCES number (id),
    FOREIGN KEY(race_id) REFERENCES race (id)
);

ALTER TABLE paddler ADD COLUMN gender VARCHAR(1);

UPDATE alembic_version SET version_num='0dc044ac3c23' WHERE alembic_version.version_num = 'c8cd8ff9c99e';
