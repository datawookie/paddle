from .http_status import *
import pytest


@pytest.mark.ui
def test_race(client):
    RACE_ID = 1

    response = client.get(f"/race/{RACE_ID}")

    assert response.status_code == HTTP_STATUS_OKAY


@pytest.mark.ui
def test_race_list(client):
    response = client.get("/")

    assert "<h1>Races</h1>" in response.text
