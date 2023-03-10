import datetime
import logging
import pytest

from . import TestRunner
from .http_status import *
import database as db

QUODPOT_MASTERS = {
    "name": "Quodpot Masters",
    "date": datetime.datetime.strptime("1997-07-13", "%Y-%m-%d").date(),
    "series_id": TestRunner.ID_SERIES_HOGWARTS,
    "time_min_start": "08:00:00",
    "time_max_start": "11:00:00",
    "time_min_finish": "10:00:00",
    "time_max_finish": "13:00:00",
}


class TestRace(TestRunner):
    @pytest.mark.ui
    def test_race(self, client):
        response = client.get(f"/race/{self.ID_RACE_QUIDDITCH_WORLD_CUP}")

        assert response.status_code == HTTP_STATUS_OKAY

    @pytest.mark.ui
    def test_race_list(self, client):
        response = client.get("/")

        assert "<h1>Races</h1>" in response.text

    @pytest.mark.ui
    def test_race_create(self, client):
        response = client.post(
            "/race/create",
            data=QUODPOT_MASTERS,
            follow_redirects=True,
        )

        assert response.status_code == HTTP_STATUS_OKAY
        assert "Quodpot Masters" in response.text

    @pytest.mark.ui
    def test_race_update(self, client, session):
        race = session.get(db.Race, self.ID_RACE_QUIDDITCH_WORLD_CUP)
        logging.info(race)

        response = client.post(
            f"/race/{self.ID_RACE_QUIDDITCH_WORLD_CUP}/update",
            data={
                "name": "Quidditch World Series",
                "date": datetime.datetime.strptime("1997-06-26", "%Y-%m-%d").date(),
                "time_min_start": "08:00:00",
                "time_max_start": "11:00:00",
                "time_min_finish": "10:00:00",
                "time_max_finish": "12:00:00",
            },
            follow_redirects=True,
        )

        assert response.status_code == HTTP_STATUS_OKAY
        assert "Quidditch World Series" in response.text

    @pytest.mark.ui
    def test_race_missing_name(self, client):
        payload = QUODPOT_MASTERS.copy()
        payload.pop("name")

        response = client.post(
            "/race/create",
            data=payload,
        )

        assert response.status_code == HTTP_STATUS_OKAY
        assert "Race name must be supplied." in response.text

    @pytest.mark.ui
    def test_race_missing_date(self, client):
        payload = QUODPOT_MASTERS.copy()
        payload.pop("date")

        response = client.post(
            "/race/create",
            data=payload,
        )

        assert response.status_code == HTTP_STATUS_OKAY
        assert "Race date must be supplied." in response.text
