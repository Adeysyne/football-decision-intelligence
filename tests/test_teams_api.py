from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app
)


def test_team_list_starts_empty():
    response = client.get(
        "/api/v1/teams"
    )

    assert response.status_code == 200

    assert response.json() == []


def test_team_list_returns_created_team():
    create_response = client.post(
        "/api/v1/teams",
        json={
            "team_name": "Dashboard FC",
            "default_formation": "4-3-3",
            "tactical_identity": (
                "Controlled possession "
                "with aggressive pressing."
            ),
        },
    )

    assert (
        create_response.status_code
        == 201
    )

    response = client.get(
        "/api/v1/teams"
    )

    assert response.status_code == 200

    teams = response.json()

    assert len(teams) == 1

    assert (
        teams[0]["team_name"]
        == "Dashboard FC"
    )

    assert (
        teams[0][
            "default_formation"
        ]
        == "4-3-3"
    )