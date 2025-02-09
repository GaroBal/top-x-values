import numpy as np
from tqdm import tqdm
import pyarrow as pa
import pyarrow.parquet as pq
import psutil


def get_optimal_chunk_size(n_entries: int, safety_factor: float = 0.5) -> int:
    """Calculate optimal chunk size based on available system memory."""
    available_memory = psutil.virtual_memory().available
    bytes_per_sample = 50  # Conservative estimate for string bytes
    max_entries_in_memory = int((available_memory * safety_factor) / bytes_per_sample)
    chunk_size = min(max_entries_in_memory, n_entries)
    return max(min(chunk_size, n_entries), 10000)


def generate_dataset_chunked(n_entries: int, output_file: str):
    """Generate dataset in chunks directly to Parquet format with memory-aware chunking"""
    chunk_size = get_optimal_chunk_size(n_entries)
    print(f"Using chunk size of {chunk_size:,} based on available memory")

    rng = np.random.default_rng()
    writer = None

    # Define maximum value to be slightly less than debug values
    max_int64 = np.iinfo(np.int64).max
    max_value = max_int64 - 10  # Ensuring generated values are less than debug values

    # Create debug pairs first
    debug_pairs = [
        f"{max_int64}_1{max_int64}",
        f"{max_int64 - 1}_1{max_int64 - 1}",
        f"{max_int64 - 2}_1{max_int64 - 2}",
        f"{max_int64 - 3}_1{max_int64 - 3}",
    ]

    try:
        # Start with debug entries
        debug_table = pa.Table.from_arrays([pa.array(debug_pairs)], names=['raw_data'])

        # Initialize writer with debug entries
        writer = pq.ParquetWriter(output_file, debug_table.schema, write_statistics=False)
        writer.write_table(debug_table)

        # Now generate and write the main data in chunks
        for chunk_start in tqdm(range(0, n_entries, chunk_size), desc="Generating chunks"):
            chunk_size_actual = min(chunk_size, n_entries - chunk_start)

            # Generate sequential IDs for this chunk
            chunk_ids = np.arange(
                chunk_start + 1,  # Start from 1
                chunk_start + chunk_size_actual + 1
            )

            # Generate random values with controlled maximum
            values = rng.integers(1, max_value, size=chunk_size_actual)

            # Create combined id_value strings
            id_value = np.char.add(
                np.char.add(
                    chunk_ids.astype(str),
                    np.full(chunk_size_actual, '_')
                ),
                values.astype(str)
            )

            # Convert to Arrow array and create table
            table = pa.Table.from_arrays([pa.array(id_value)], names=['raw_data'])
            writer.write_table(table)

            # Clean up memory
            del chunk_ids, values, id_value, table

    finally:
        if writer:
            writer.close()


# Configuration
N_ENTRIES = 10000000
OUTPUT_FILE = "data_sample.parquet"

print("Starting dataset generation...")
generate_dataset_chunked(N_ENTRIES, OUTPUT_FILE)
print(f"Generated debug entries + {N_ENTRIES} entries to {OUTPUT_FILE}")

# Print first 10 values for verification
print("\nFirst 10 values in the generated file:")
table = pq.read_table(OUTPUT_FILE, columns=['raw_data'])
for i, value in enumerate(table['raw_data'].slice(0, 10).to_pylist()):
    print(f"{i+1}. {value}")