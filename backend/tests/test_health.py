from django.test import TestCase, Client
from django.urls import reverse

class HealthCheckEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_returns_200_and_service_info(self):
        """Test GET /api/v1/health/ returns status ok and service identifier."""
        response = self.client.get(reverse('api-health'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('service'), 'real-estate-backend')
        self.assertEqual(data.get('version'), '1.0.0-scaffold')
