"""
test_plants.py — Tests for the Plants API endpoints (CRUD + search).
"""

PLANT = {
    "common_name": "Test Basil",
    "scientific_name": "Ocimum testus",
    "family": "Lamiaceae",
    "description": "A plant used only in tests.",
}


class TestPlantsAPI:
    def test_create_get_update_delete_roundtrip(self, client):
        created = client.post("/api/v1/plants/", json=PLANT)
        assert created.status_code == 201
        plant_id = created.json()["id"]

        fetched = client.get(f"/api/v1/plants/{plant_id}")
        assert fetched.status_code == 200
        assert fetched.json()["scientific_name"] == PLANT["scientific_name"]

        updated = client.put(f"/api/v1/plants/{plant_id}", json={"habitat": "Test garden"})
        assert updated.status_code == 200
        assert updated.json()["habitat"] == "Test garden"
        assert updated.json()["common_name"] == PLANT["common_name"]  # untouched

        assert client.delete(f"/api/v1/plants/{plant_id}").status_code == 204
        assert client.get(f"/api/v1/plants/{plant_id}").status_code == 404

    def test_duplicate_scientific_name_returns_409(self, client):
        first = client.post("/api/v1/plants/", json={**PLANT, "scientific_name": "Ocimum dupus"})
        assert first.status_code == 201
        second = client.post("/api/v1/plants/", json={**PLANT, "scientific_name": "ocimum DUPUS"})
        assert second.status_code == 409
        client.delete(f"/api/v1/plants/{first.json()['id']}")

    def test_list_and_search(self, client):
        created = client.post(
            "/api/v1/plants/",
            json={**PLANT, "common_name": "Searchable Sage", "scientific_name": "Salvia searchus"},
        ).json()
        listing = client.get("/api/v1/plants/")
        assert listing.status_code == 200
        assert any(p["id"] == created["id"] for p in listing.json())

        found = client.get("/api/v1/plants/search", params={"q": "searchable"})
        assert [p["id"] for p in found.json()] == [created["id"]]
        assert client.get("/api/v1/plants/search", params={"q": "zzzznomatch"}).json() == []
        client.delete(f"/api/v1/plants/{created['id']}")

    def test_get_nonexistent_plant_returns_404(self, client):
        response = client.get("/api/v1/plants/999999")
        assert response.status_code == 404
        assert response.json()["success"] is False

    def test_validation_error_returns_422(self, client):
        assert client.post("/api/v1/plants/", json={"common_name": ""}).status_code == 422
