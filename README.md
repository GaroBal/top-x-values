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


1. Generate the dataset that will be used by the application:
    ```sh
    python3 data_script.py
    ```

2. To run the application, use the following command:
    ```sh
    python3 main.py
    ```

3. To make a request to the application, use the following command:
    ```sh
    curl -L 'http://localhost:8000/api/top-values?x=10'
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