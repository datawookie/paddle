from . import TestRunner
from .http_status import *
import database as db


class TestSeries(TestRunner):
    def test_series_results(self, client, session):
        response = client.get(
            f"/series/{self.ID_SERIES_HOGWARTS}",
        )

        assert response.status_code == HTTP_STATUS_OKAY

        series = session.get(db.Series, self.ID_SERIES_HOGWARTS)

        assert f"<h1>{series.name} Series</h1>" in response.text
