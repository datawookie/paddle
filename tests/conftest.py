import datetime
import logging
import os
import tempfile

import pytest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)7s] %(message)s",
)

# Temporary file for database.
#
_, DB_PATH = tempfile.mkstemp(".db")
#
os.environ["CONNECTION_STRING"] = f"sqlite:///{DB_PATH}"

import database as db  # noqa: E402
from paddle import factory  # noqa: E402


@pytest.fixture(scope="class")
def database():
    logging.info("Recreate database from scratch.")
    # Recreate database from scratch.
    db.Base.metadata.drop_all(db.engine)
    db.Base.metadata.create_all(db.engine)
    logging.info("Done!")
    logging.info("Create database session.")
    session = db.Session()
    logging.info("Done.")

    yield session
    session.close()


@pytest.fixture(scope="class")
def session(database):
    session = database

    db.Base.metadata.create_all(db.engine)
    session = db.Session()

    session.add(db.Series(name="Hogwarts"))

    session.add(
        db.Race(
            name="Quidditch World Cup",
            date=datetime.datetime.strptime("1997-06-26", "%Y-%m-%d").date(),
            series_id=1,
            time_min_start="08:00:00",
            time_max_start="10:00:00",
            time_min_finish="09:00:00",
            time_max_finish="12:00:00",
        )
    )

    session.add(db.Club(code_regex="GRY|GFR", name="Gryffindor"))
    session.add(db.Club(code_regex="HUF", name="Hufflepuff"))

    session.add(db.TeamType(label="Junior"))
    session.add(db.TeamType(label="Senior"))

    for category in db.CATEGORY_LIST:
        session.add(db.Category(label=category))

    for number in range(1, 21):
        session.add(db.Number(id=number))

    session.commit()

    yield session


@pytest.fixture
def app(session):
    app = factory()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app

    # Delete testing database.
    # os.unlink(DB_PATH)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
