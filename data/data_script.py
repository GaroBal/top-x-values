import os

import numpy as np
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm

"""
Script ran to generate locally used data for testing purposes.

- Implemented Memory Aware Chunking to generate large datasets without running out of memory.

Future Improvements:
- Write directly to S3 Bucket to generate an extremely large dataset.
"""


def get_optimal_chunk_size(n_entries: int, safety_factor: float = 0.5) -> int:
    """Calculate optimal chunk size based on available system memory."""
    available_memory = psutil.virtual_memory().available
    bytes_per_sample = 50  # Conservative estimate for string bytes
    max_entries_in_memory = int((available_memory * safety_factor) / bytes_per_sample)
    chunk_size = min(max_entries_in_memory, n_entries)
    return max(min(chunk_size, n_entries), 10000)


def generate_dataset_chunked(n_entries: int, output_file: str):
    """Generate dataset in chunks directly to Parquet format with memory-aware chunking"""
    # Delete existing file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    chunk_size = get_optimal_chunk_size(n_entries)
    print(f"Using chunk size of {chunk_size:,} based on available memory")

    rng = np.random.default_rng()
    writer = None

    # Define maximum value to be slightly less than debug values
    max_int64 = np.iinfo(np.int64).max
    max_value = max_int64 - 10  # Ensuring generated values are less than debug values

    # Create debug pairs first
    debug_pairs_start = [
        f"1_{max_int64}",
        f"2_{max_int64 - 1}",
        f"3_{max_int64 - 2}",
        f"4_{max_int64 - 3}",
    ]

    debug_pairs_end = [
        f"5_{max_int64 -4}",
        f"6_{max_int64 - 5}",
        f"7_{max_int64 - 6}",
        f"8_{max_int64 - 7}",
    ]

    try:
        # Start with debug entries
        debug_table_start = pa.Table.from_arrays(
            [pa.array(debug_pairs_start)], names=["raw_data"]
        )

        # Initialize writer with debug entries
        writer = pq.ParquetWriter(
            output_file, debug_table_start.schema, write_statistics=False
        )
        writer.write_table(debug_table_start)

        # Now generate and write the main data in chunks
        for chunk_start in tqdm(
            range(10, n_entries, chunk_size), desc="Generating chunks"
        ):
            chunk_size_actual = min(chunk_size, n_entries - chunk_start)

            # Generate sequential IDs for this chunk
            chunk_ids = np.arange(
                chunk_start + 1, chunk_start + chunk_size_actual + 1  # Start from 1
            )

            # Generate random values with controlled maximum
            values = rng.integers(1, max_value, size=chunk_size_actual)

            # Create combined id_value strings
            id_value = np.char.add(
                np.char.add(chunk_ids.astype(str), np.full(chunk_size_actual, "_")),
                values.astype(str),
            )

            # Convert to Arrow array and create table
            table = pa.Table.from_arrays([pa.array(id_value)], names=["raw_data"])
            writer.write_table(table)

            # Clean up memory
            del chunk_ids, values, id_value, table

            # Write debug pairs end
            debug_table_end = pa.Table.from_arrays(
                [pa.array(debug_pairs_end)], names=["raw_data"]
            )
            writer.write_table(debug_table_end)

    finally:
        if writer:
            writer.close()


# Configuration for different dataset sizes
datasets = {
    "small": 1000000,  # 1M
    "medium": 10000000,  # 10M
    "large": 100000000,  # 100M
}

for size, n_entries in datasets.items():
    output_file = f"data/data_sample_{size}.parquet"
    print(f"Starting dataset generation for {size} dataset...")
    generate_dataset_chunked(n_entries, output_file)
    print(f"Generated {size} dataset with {n_entries} entries to {output_file}")
