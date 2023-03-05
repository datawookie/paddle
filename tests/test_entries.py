from pathlib import Path
import pytest

from .http_status import *

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
