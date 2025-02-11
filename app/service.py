import multiprocessing
from pathlib import Path
from typing import List

from dask.distributed import Client

from app.exceptions import DataProcessingError, DataValidationError
from app.profiling import profile_context
from app.utils import read_dataframe, validate_and_extract_value


class DataService:
    """
    Service class for processing large datasets using Dask.
    Determines the Top X Values in the given dataset.

    Future improvements:
    - Read the dataset from an S3 bucket, to be able to process extremely large datasets.
    - Evaluate different partition sizes to optimize performance based on profiler data collected.
    - Evaluate possible alternative strategies for processing the data, such as probabilistic approaches or statistical methods
    - Possibly implement said strategies in a hybrid approach to account for different data sizes and requested Top X values.
    """
    DEFAULT_WORKERS = max(1, multiprocessing.cpu_count() - 1)

    def __init__(
        self,
        data_path: str,
        partition_size: str = "64MB",
    ):
        """
        Args:
            data_path: Path to parquet file
            partition_size: Size of Dask partitions
        """
        if not data_path:
            raise ValueError("Data path must be provided")

        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise ValueError(f"Data path does not exist: {data_path}")

        self.partition_size = partition_size

        try:
            self.client = Client(n_workers=self.DEFAULT_WORKERS)
        except Exception as e:
            raise DataProcessingError(f"Failed to initialize Dask client: {str(e)}")

    def get_top_values(self, x: int) -> List[int]:
        """
        Get Top X Values using Dask's nlargest functionality.

        Args:
            x: Number of top values to return

        Returns:
            List of top X IDs
        """
        try:
            with profile_context("read_dataframe"):
                df = read_dataframe(
                    data_path=self.data_path, partition_size=self.partition_size
                )

            with profile_context("compute_value_column"):
                # Add computed value column with proper error handling
                df["value"] = df["raw_data"].map(
                    validate_and_extract_value, meta=("value", "int64")
                )

            with profile_context("partition_tops"):
                # First get top X values per partition
                per_partition_tops = df.map_partitions(
                    lambda pdf: pdf.nlargest(x, "value")
                )

            with profile_context("global_tops"):
                # Then get global top X from the per-partition results
                top_rows = per_partition_tops.nlargest(x, "value").compute()

            with profile_context("extract_ids"):
                # Extract and validate IDs
                result = []
                for raw_data in top_rows["raw_data"]:
                    parts = raw_data.split("_")
                    if len(parts) != 2:
                        raise DataValidationError(
                            f"Invalid data format. Expected 'id_value', got '{raw_data}'"
                        )
                    try:
                        result.append(int(parts[0]))
                    except ValueError:
                        raise DataValidationError(
                            f"Invalid ID format in '{raw_data}': expected integer"
                        )

                return result

        except (DataValidationError, DataProcessingError) as e:
            raise e
        except Exception as e:
            raise DataProcessingError(f"Unexpected error processing data: {str(e)}")

    def __del__(self):
        """Cleanup Dask client if it exists."""
        try:
            if hasattr(self, "client"):
                self.client.close()
        except Exception:
            pass  # Suppress errors during cleanup
