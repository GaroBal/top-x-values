import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch

from app.exceptions import DataProcessingError
from app.service import DataService


class TestDataService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create test data and save as parquet file before running tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_data_path = Path(cls.test_dir) / "test_data.parquet"

        # Create test dataset with known values
        np.random.seed(42)  # For reproducibility
        n_rows = 1000

        # Generate random IDs and values
        ids = np.arange(10000000, 10000000 + n_rows - 10)  # Reserve space for our explicit entries
        values = np.random.randint(1, 800, size=len(ids))  # Lower max value for random entries

        # Create explicit high-value entries that should always be at the top
        explicit_pairs = [
            (10000990, 999),  # Highest
            (10000991, 998),  # Second highest
            (10000992, 997),  # Third highest
            (10000993, 996),  # Fourth highest
            (10000994, 995),  # Fifth highest
            (10000995, 994),  # Sixth highest
            (10000996, 993),  # Seventh highest
            (10000997, 992),  # Eighth highest
            (10000998, 991),  # Ninth highest
            (10000999, 990),  # Tenth highest
        ]

        # Add explicit entries to our data
        explicit_ids = [pair[0] for pair in explicit_pairs]
        explicit_values = [pair[1] for pair in explicit_pairs]

        # Combine random and explicit data
        all_ids = np.concatenate([ids, explicit_ids])
        all_values = np.concatenate([values, explicit_values])

        # Create raw_data column in required format
        raw_data = [f"{id_}_{value}" for id_, value in zip(all_ids, all_values)]

        # Create DataFrame and save as parquet
        df = pd.DataFrame({
            'raw_data': raw_data
        })
        df.to_parquet(cls.test_data_path)

        # Store known values for testing
        cls.known_values = sorted([(value, id_) for id_, value in zip(all_ids, all_values)], reverse=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test directory after all tests."""
        shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Set up DataService instance before each test."""
        self.service = DataService(str(self.test_data_path))

    def tearDown(self):
        """Clean up after each test."""
        self.service.__del__()

    def test_init_with_invalid_path(self):
        """Test initialization with invalid data path."""
        with self.assertRaises(ValueError):
            DataService("")

    def test_init_with_nonexistent_path(self):
        """Test initialization with non-existent data path."""
        with self.assertRaises(ValueError):
            DataService("nonexistent.parquet")

    @patch('app.service.Client')
    def test_init_client_error(self, mock_client):
        """Test handling of Dask client initialization error."""
        mock_client.side_effect = Exception("Client initialization failed")
        with self.assertRaises(DataProcessingError):
            DataService(str(self.test_data_path))

    def test_get_top_values_success(self):
        """Test successful retrieval of top values with actual data."""
        # Test different values of X
        for x in [1, 5, 10]:
            with self.subTest(x=x):
                result = self.service.get_top_values(x)

                # Check length of result
                self.assertEqual(len(result), x)

                # Get expected top X IDs from our known values
                expected_ids = [id_ for _, id_ in self.known_values[:x]]

                # Convert result to set for comparison (since order doesn't matter)
                self.assertEqual(set(result), set(expected_ids))

    def test_get_top_values_success_with_duplicates(self):
        """Test handling of duplicate values."""
        # Create temporary data with duplicate values
        temp_path = Path(self.test_dir) / "test_duplicates.parquet"
        df = pd.DataFrame({
            'raw_data': [
                '10000001_100',
                '10000002_100',  # Same value as above
                '10000003_50',
                '10000004_25'
            ]
        })
        df.to_parquet(temp_path)

        service = DataService(str(temp_path))
        result = service.get_top_values(2)

        # Both IDs with value 100 should be in result
        self.assertEqual(len(result), 2)
        self.assertTrue(all(id_ in [10000001, 10000002] for id_ in result))
        service.__del__()


    def test_get_top_values_success_large_x(self):
        """Test requesting more values than available in dataset."""
        x = 2000  # Larger than our test dataset
        result = self.service.get_top_values(x)
        self.assertEqual(len(result), min(x, len(self.known_values)))

