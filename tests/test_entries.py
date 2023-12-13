from pathlib import Path

import pytest

import database as db

from . import TestRunner
from .http_status import *

resources = Path(__file__).parent / "resources"


class TestEntry(TestRunner):
    @pytest.mark.ui
    def test_entries_import_xlsx_without_dob(self, client):
        response = client.post(
            f"/race/{self.ID_RACE_QUIDDITCH_WORLD_CUP}/entries/import/xlsx",
            data={
                "file": (resources / "entries-without-dob.xlsx").open("rb"),
            },
        )
        assert response.status_code == HTTP_STATUS_FOUND

    @pytest.mark.ui
    def test_entries_import_xlsx_unknown_club(self, client, session):
        entries_count = session.query(db.Entry).count()

        response = client.post(
            f"/race/{self.ID_RACE_QUIDDITCH_WORLD_CUP}/entries/import/xlsx",
            data={
                "file": (resources / "entries-unknown-club.xlsx").open("rb"),
            },
        )
        assert response.status_code == HTTP_STATUS_NOT_FOUND

        # Check that all entries are rolled back.
        assert entries_count == session.query(db.Entry).count()
