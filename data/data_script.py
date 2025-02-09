import numpy as np
from tqdm import tqdm


def generate_dataset_chunked(n_samples: int, output_file: str, chunk_size: int = 100000):
    """Generate dataset in chunks with improved memory and performance efficiency"""

    id_range_min = 10000000
    id_range_max = 99999999
    value_range_min = 10
    value_range_max = 10000001

    # Calculate total possible IDs
    total_possible_ids = id_range_max - id_range_min + 1
    if n_samples > total_possible_ids:
        raise ValueError("Requested samples exceed possible unique IDs")

    rng = np.random.default_rng()

    with open(output_file, 'w', buffering=8192) as f:
        for chunk_start in tqdm(range(0, n_samples, chunk_size), desc="Generating chunks"):
            chunk_size_actual = min(chunk_size, n_samples - chunk_start)

            # Keep the original unique ID generation method
            chunk_ids = rng.choice(
                np.arange(id_range_min, id_range_max + 1),
                size=chunk_size_actual,
                replace=False
            )

            # Generate values
            values = rng.integers(
                value_range_min,
                value_range_max,
                size=chunk_size_actual
            )

            # Use numpy's fast batch writing instead of string formatting
            np.savetxt(f,
                       np.column_stack((chunk_ids, values)),
                       fmt='%d_%d',
                       delimiter='',
                       newline='\n')

            del chunk_ids, values


# Configuration
N_SAMPLES = 1000000
OUTPUT_FILE = "data_sample.csv"
CHUNK_SIZE = 100000

print("Starting dataset generation...")
generate_dataset_chunked(N_SAMPLES, OUTPUT_FILE, CHUNK_SIZE)

# Debug entries
debug_pairs = [
    ("199999999", 110000001),
    ("299999999", 1110000001),
    ("399999999", 1110000001),
    ("499999999", 110000001)
]

print("Adding debug entries...")
with open(OUTPUT_FILE, 'a', buffering=8192) as f:
    debug_lines = []
    for id_, value in debug_pairs:
        debug_lines.append(f"{id_}_{value}\n")
    f.writelines(debug_lines)

print(f"Generated {N_SAMPLES} samples + debug entries to {OUTPUT_FILE}")