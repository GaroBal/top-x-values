import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from main import app


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ping_endpoint(self):
        response = self.client.get("/api/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "pong")

    @patch("app.handler.DataService")
    def test_top_values_endpoint_success(self, mock_service):
        # Setup mock
        mock_instance = Mock()
        mock_instance.get_top_values.return_value = [5, 4, 3]
        mock_service.return_value = mock_instance

        # Test with default data path
        response = self.client.get("/api/top-values/?x=3")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [5, 4, 3])
        mock_instance.get_top_values.assert_called_once_with(3)

    @patch("app.handler.DataService")
    def test_top_values_with_custom_path(self, mock_service):
        # Setup mock
        mock_instance = Mock()
        mock_instance.get_top_values.return_value = [10, 9]
        mock_service.return_value = mock_instance

        # Test with custom data path
        response = self.client.get("/api/top-values/?x=2&data_path=data.parquet")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [10, 9])
        mock_service.assert_called_once_with(data_path="data.parquet")

    @patch("app.handler.DataService")
    def test_top_values_default_path(self, mock_service):
        # Setup mock
        mock_instance = Mock()
        mock_instance.get_top_values.return_value = [10, 9]
        mock_service.return_value = mock_instance

        # Make request without specifying data_path
        response = self.client.get("/api/top-values/?x=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [10, 9])
        # Verify DataService was instantiated with the default path
        mock_service.assert_called_once_with(data_path="data/data_sample.parquet")

    def test_top_values_invalid_x(self):
        # Test with invalid x value (less than or equal to 0)
        response = self.client.get("/api/top-values/?x=0")
        self.assertEqual(response.status_code, 422)

        response = self.client.get("/api/top-values/?x=-1")
        self.assertEqual(response.status_code, 422)

    def test_top_values_missing_x(self):
        # Test without providing x parameter
        response = self.client.get("/api/top-values/")
        self.assertEqual(response.status_code, 422)
