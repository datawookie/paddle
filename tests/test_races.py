import logging


def test_race_list(client):
    response = client.get("/")
    assert "<h1>Races</h1>" in response.text
