"""E2E tests for events."""

from json import loads

class TestE2EEvent:
    def test_should_create_and_fetch(self, client):
        response_create = client.post(
            "/event/",
            json={
                  "userId": "user123",
                  "date": "2025-04-14",
                  "time": "20:43",
                  "description": "Test Description"
            }
        )

        assert response_create.status_code == 201

        response_get = client.get(
            "/event/"
        )

        assert response_get.status_code == 200

        result = loads(response_get.text)
        assert len(result) >= 1

