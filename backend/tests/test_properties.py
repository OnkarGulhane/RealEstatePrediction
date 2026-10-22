import pytest
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestPropertiesMetadata:
    def setup_method(self):
        self.client = APIClient()

    def test_locations_metadata_public_and_complete(self):
        url = "/api/v1/locations/"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["schema_version"] == "1.0"
        assert data["total_locations"] == 81
        assert len(data["locations"]) == 81

        # Check sample locations and structure
        loc_names = [loc["name"] for loc in data["locations"]]
        assert "Mumbai" in loc_names
        assert "Bangalore" in loc_names
        assert "Pune" in loc_names
        assert "Zirakpur" in loc_names
        assert "Agra" in loc_names

        # Each location has name and normalized
        first_loc = data["locations"][0]
        assert "name" in first_loc
        assert "normalized" in first_loc
        assert first_loc["normalized"] == first_loc["name"].lower()

        # Categorical metadata
        assert "area_bases" in data
        assert set(data["area_bases"]) == {"CARPET", "SUPER"}

        assert "categories" in data
        cats = data["categories"]
        assert "furnishing" in cats
        assert "transaction_type" in cats
        assert "status" in cats
        assert "facing" in cats
        assert "ownership" in cats

        assert "Semi-Furnished" in cats["furnishing"]
        assert "Ready to Move" in cats["status"]
        assert "Freehold" in cats["ownership"]
