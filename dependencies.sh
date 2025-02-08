#!/bin/bash

# Ensure the script stops on errors
set -e

echo "Cleaning up previous virtual environment (if any)..."
# Remove the virtual environment if it exists
if [ -d "venv" ]; then
    rm -rf venv
    echo "Old virtual environment removed."
fi

echo "Setting up dependencies..."

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create a new virtual environment
echo "Creating a new virtual environment..."
python3 -m venv venv

# Upgrade pip to the latest version
echo "Upgrading pip..."
venv/bin/pip3 install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing dependencies..."
venv/bin/pip3 install -r requirements.txt

echo "Dependencies installed successfully!"
echo "Activating virtual environment..."

# Activate the virtual environment
source venv/bin/activate  # For Linux/macOS

echo "Virtual environment activated. You can now run your application."