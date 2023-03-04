from .http_status import *
import database as db


def test_series_results(client, session):
    SERIES_ID = 1

    response = client.get(
        f"/series/{SERIES_ID}",
    )

    assert response.status_code == HTTP_STATUS_OKAY

    series = session.get(db.Series, SERIES_ID)

    assert f"<h1>{series.name} Series</h1>" in response.text
