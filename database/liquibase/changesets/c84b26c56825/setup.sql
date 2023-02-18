--liquibase formatted sql
--changeset datawookie:c84b26c56825
--precondition-sql-check expectedResult:1 SELECT COUNT(*) FROM alembic_version WHERE version_num = '8d8d70c226fa'

-- Running upgrade 8d8d70c226fa -> c84b26c56825

CREATE TABLE announcement (
    id INTEGER NOT NULL,
    text VARCHAR,
    enabled BOOLEAN,
    PRIMARY KEY (id)
);
--rollback DROP TABLE announcement;

CREATE TABLE category (
    id INTEGER NOT NULL,
    label VARCHAR,
    PRIMARY KEY (id),
    CONSTRAINT uq_category_label UNIQUE (label)
);
--rollback DROP TABLE category;

CREATE TABLE club (
    id VARCHAR(3) NOT NULL,
    name VARCHAR,
    PRIMARY KEY (id)
);
--rollback DROP TABLE club;

CREATE TABLE member (
    id INTEGER NOT NULL,
    first VARCHAR,
    middle VARCHAR,
    last VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE number (
    id INTEGER NOT NULL,
    lost BOOLEAN,
    PRIMARY KEY (id)
);

CREATE TABLE paddler (
    id INTEGER NOT NULL,
    bcu INTEGER,
    bcu_expiry DATE,
    division INTEGER,
    title VARCHAR,
    first VARCHAR,
    middle VARCHAR,
    last VARCHAR,
    suffix VARCHAR,
    dob DATE,
    address VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    emergency_name VARCHAR,
    emergency_phone VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE series (
    id INTEGER NOT NULL,
    name VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE time_trial (
    id INTEGER NOT NULL,
    date DATE,
    distance NUMERIC,
    PRIMARY KEY (id)
);

CREATE TABLE user (
    id INTEGER NOT NULL,
    email VARCHAR,
    pwd VARCHAR,
    authenticated BOOLEAN,
    PRIMARY KEY (id)
);

CREATE TABLE race (
    id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    date DATE NOT NULL,
    series_id INTEGER,
    time_min_start VARCHAR,
    time_max_start VARCHAR,
    time_min_finish VARCHAR,
    time_max_finish VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY(series_id) REFERENCES series (id),
    CONSTRAINT uq_race_name_date UNIQUE (name, date)
);

CREATE INDEX ix_race_series_id ON race (series_id);

CREATE TABLE team_type (
    id INTEGER NOT NULL,
    label VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE team (
    id INTEGER NOT NULL,
    name VARCHAR,
    team_type_id INTEGER,
    series_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(team_type_id) REFERENCES team_type (id),
    FOREIGN KEY(series_id) REFERENCES series (id),
    CONSTRAINT uq_team_name_series UNIQUE (name, series_id)
);

CREATE INDEX ix_team_series_id ON team (series_id);

CREATE TABLE time_trial_result (
    id INTEGER NOT NULL,
    time_trial_id INTEGER,
    member_id INTEGER,
    time VARCHAR,
    PRIMARY KEY (id),
    FOREIGN KEY(member_id) REFERENCES member (id),
    FOREIGN KEY(time_trial_id) REFERENCES time_trial (id)
);

CREATE INDEX ix_time_trial_result_member_id ON time_trial_result (member_id);

CREATE INDEX ix_time_trial_result_time_trial_id ON time_trial_result (time_trial_id);

CREATE TABLE entry (
    id INTEGER NOT NULL,
    race_id INTEGER,
    category_id INTEGER,
    boat_type VARCHAR(2),
    entry_number INTEGER,
    online BOOLEAN,
    series BOOLEAN,
    series_id INTEGER,
    time_start VARCHAR,
    time_finish VARCHAR,
    time_adjustment INTEGER,
    registered BOOLEAN NOT NULL,
    retired BOOLEAN NOT NULL,
    scratched BOOLEAN NOT NULL,
    disqualified BOOLEAN NOT NULL,
    note TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY(category_id) REFERENCES category (id),
    FOREIGN KEY(race_id) REFERENCES race (id),
    FOREIGN KEY(series_id) REFERENCES series (id)
);

CREATE INDEX ix_entry_boat_type ON entry (boat_type);

CREATE INDEX ix_entry_category_id ON entry (category_id);

CREATE INDEX ix_entry_race_id ON entry (race_id);

CREATE INDEX ix_entry_series_id ON entry (series_id);

CREATE TABLE crew (
    id INTEGER NOT NULL,
    paddler_id INTEGER,
    club_id VARCHAR(3),
    entry_id INTEGER,
    team_id INTEGER,
    services BOOLEAN DEFAULT 0,
    due NUMERIC,
    paid NUMERIC,
    PRIMARY KEY (id),
    FOREIGN KEY(club_id) REFERENCES club (id),
    FOREIGN KEY(entry_id) REFERENCES entry (id),
    FOREIGN KEY(paddler_id) REFERENCES paddler (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE INDEX ix_crew_club_id ON crew (club_id);

CREATE INDEX ix_crew_entry_id ON crew (entry_id);

CREATE INDEX ix_crew_paddler_id ON crew (paddler_id);

CREATE INDEX ix_crew_team_id ON crew (team_id);

CREATE TABLE number_entry (
    id INTEGER NOT NULL,
    number_id INTEGER NOT NULL,
    entry_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(entry_id) REFERENCES entry (id),
    FOREIGN KEY(number_id) REFERENCES number (id)
);

UPDATE alembic_version SET version_num='c84b26c56825' WHERE alembic_version.version_num = '8d8d70c226fa';
