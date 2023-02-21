from .http_status import *
import database as db


def test_team_add(client, session):
    TEAM_NAME = "Harry's Heros"
    TEAM_TYPE_ID = 1
    TEAM_SERIES_ID = 1

    response = client.post(
        "/team/create",
        data={"name": TEAM_NAME, "team_type": TEAM_TYPE_ID, "series": TEAM_SERIES_ID},
    )
    assert response.status_code == HTTP_STATUS_FOUND

    team = session.query(db.Team).filter(db.Team.name == TEAM_NAME).one()

    assert team
    assert team.name == TEAM_NAME
    assert team.team_type_id == TEAM_TYPE_ID
    assert team.series_id == TEAM_SERIES_ID
