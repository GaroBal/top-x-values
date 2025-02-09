import os
import tempfile
import unittest

from app.service import DataService


class TestDataService(unittest.TestCase):
    def test_get_top_values_small_dataset(self):
        # Create a small CSV file
        data = ["1_100", "2_200", "3_50", "4_300"]
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write("\n".join(data))
            data_path = f.name

        service = DataService(data_path)

        result = service.get_top_values(2)

        self.assertEqual(sorted(result), sorted([2, 4]))

        # Clean up
        os.remove(data_path)
