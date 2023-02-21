import os
import tempfile
import logging
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
from kanoe import factory  # noqa: E402


@pytest.fixture(scope="session")
def database():
    db.Base.metadata.create_all(db.engine)
    session = db.Session()

    yield session
    session.close()


@pytest.fixture(scope="session")
def session(database):
    session = database

    db.Base.metadata.create_all(db.engine)
    session = db.Session()

    session.add(db.Series(name="Series"))

    session.add(db.Club(id="GRY", name="Gryffindor"))
    session.add(db.Club(id="HUF", name="Hufflepuff"))

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
