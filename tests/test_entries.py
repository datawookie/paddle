from pathlib import Path
import pytest

from .http_status import *
import database as db

resources = Path(__file__).parent / "resources"


@pytest.mark.ui
def test_entries_import_xlsx(client):
    RACE_ID = 1

    response = client.post(
        f"/race/{RACE_ID}/entries/import/xlsx",
        data={
            "file": (resources / "entries.xlsx").open("rb"),
        },
    )
    assert response.status_code == HTTP_STATUS_FOUND


@pytest.mark.ui
def test_entries_import_xlsx_unknown_club(client, session):
    entries_count = session.query(db.Entry).count()

    RACE_ID = 1

    response = client.post(
        f"/race/{RACE_ID}/entries/import/xlsx",
        data={
            "file": (resources / "entries-unknown-club.xlsx").open("rb"),
        },
    )
    assert response.status_code == HTTP_STATUS_NOT_FOUND

    # Check that all entries are rolled back.
    assert entries_count == session.query(db.Entry).count()
