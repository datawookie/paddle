-- Running upgrade 0dc044ac3c23 -> 68cf0f59baf7

CREATE TABLE team_paddler (
    id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    paddler_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(paddler_id) REFERENCES paddler (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE INDEX ix_team_paddler_paddler_id ON team_paddler (paddler_id);

CREATE INDEX ix_team_paddler_team_id ON team_paddler (team_id);

UPDATE alembic_version SET version_num='68cf0f59baf7' WHERE alembic_version.version_num = '0dc044ac3c23';
