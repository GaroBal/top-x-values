# Top-X-Values

## Setup Instructions



### Prerequisites

- Ensure you have Python 3.9 or higher installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Clone the Repository

1. Clone the repository to your local machine using the following command:
    ```sh
    git clone https://github.com/GaroBal/top-x-values.git
    ```
2. Navigate to the project directory:
    ```sh
    cd top-x-values
    ```

### Install Dependencies

1. Create a virtual environment, and install the dependencies using the following command:
    ```sh
    source ./dependencies.sh
    ```

### Running the Application


1. Generate the dataset that will be used by the application (approx. 2.5 GB, 1.5 min to generate):
    ```sh
    python3 data_script.py
    ```

2. To run the application, use the following command:
    ```sh
    python3 main.py
    ```

3. To make a request to the application, use the following command:
    ```sh
    curl -L 'http://localhost:8000/api/top-values?x=10&data_path=<path_to_data_file>'
    ```

### Running Tests

1. To run the tests, use the following command:
    ```sh
    python3 -m unittest discover -s tests
    ```

### Linting and Formatting

1. To check code formatting with `black`:
    ```sh
    black --check . --exclude venv
    ```
2. To check import sorting with `isort`:
    ```sh
    isort --check-only . --skip venv
    ```
3. To run `flake8` for linting:
    ```sh
    flake8 . --exclude venv
    ```
   
### Visualizing the Performance

1. To visualize the performance of the application, use the following command:
    ```sh
    snakeviz profiles/<timestamp>/get_top_values.stats
    ```
   

### Code Commentary

Breaking down the implementation's complexity per key component, where:
N = number of lines in the dataset
X = number of top values to find
P = number of partitions

#### Time Complexity

Reading and extracting the values from the dataset has a time complexity of O(N) due to having to read each line in the dataset.

Finding the top X values per partition, which results in O(N/P * log X) time complexity.
But since we do this for every partition, the overall time complexity is O(N * log X).

For the second step, we need to find the top X values from the top X values of each partition.
This has a time complexity of O(PX * log X).

Therefore, the overall time complexity of the application is O(N + N * log X + PX * log X).
The dominant term is O(N * log X) here.

Very candidly, this is not the most efficient way to find the top X values, as it is not scalable for large datasets.
Something more efficient would be QuickSelect, which should have a time complexity of O(N) in the average case.
However I can't say I am comfortable with implementing the QuickSelect algorithm because of my inexperience with it.
So despite the inefficiency, I chose to implement the current solution as it is more familiar to me.

#### Space Complexity

The size of a single partition is 64MB, manually set in the code. (Reason being, I wanted to have the size be dynamic based on profiling stats, but I did not succeed in doing so.)
Each partition is loaded into memory, processed, and subsequently released, so we have a constant space complexity of O(1).

When we start the two-step process of finding the top X values, we store the top X values of each partition in a list.
Resulting in a space complexity of O(PX), as we build the top X list for each partition.

Following this, we work with this O(PX) list to find the top X values from the top X values globally.
This has a space complexity of O(X), as we only need to store the top X values globally.

Therefore, the overall space complexity of the application is O(1 + PX + X).
The dominant term is O(PX) here.

However, in the worst case, where X = N, the space complexity of the application is O(N) due to the need to store all the values in the dataset.


### Reflection

I enjoyed the challenge that the case study provided, and how it helped me to think about my knowledge gaps.

