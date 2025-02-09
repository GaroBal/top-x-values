from typing import List
import dask.dataframe as dd
import pandas as pd


class DataService:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def get_top_values(self, x: int) -> List[int]:
        """
        Get top X values from the dataset.
        """
        # Read CSV in chunks using Dask
        df = dd.read_csv(
            self.data_path,
            header=None,
            names=['raw_data'],
            blocksize='64MB'
        )

        # Process chunks
        def process_chunk(chunk):
            chunk[['id', 'value']] = chunk['raw_data'].str.split('_', expand=True)
            chunk['id'] = chunk['id'].astype(int)
            chunk['value'] = chunk['value'].astype(int)
            return chunk[['id', 'value']]

        # Define meta for the output DataFrame
        meta = pd.DataFrame({'id': pd.Series(dtype='int'), 'value': pd.Series(dtype='int')})

        processed_df = df.map_partitions(process_chunk, meta=meta)
        # Get top X values from each partition
        tops_per_partition = processed_df.map_partitions(
            lambda partition: partition.nlargest(x, 'value'),
            enforce_metadata=False
        )

        # Compute final results and get overall top X
        final_df = tops_per_partition.compute()
        result = final_df.nlargest(x, 'value')['id'].tolist()

        return result