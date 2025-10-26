#!/bin/bash

# Setup script for dimple_utils virtual environment
# This creates a virtual environment specifically for the dimple_utils submodule

set -e  # Exit on any error

echo "=== Setting up dimple_utils virtual environment ==="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run this script from the dimple_utils directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt

# Install dimple_utils in development mode
echo "Installing dimple_utils in development mode..."
pip3 install -e .

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the example script:"
echo "  python examples/example_openai_class.py"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
