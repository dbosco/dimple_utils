#!/bin/bash

# Activation script for dimple_utils virtual environment
# This activates the virtual environment and sets up the Python path

echo "Activating dimple_utils virtual environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run setup_venv.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Add current directory to Python path for imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Virtual environment activated!"
echo "Python path updated to include current directory."
echo ""
echo "You can now run:"
echo "  python examples/example_openai_class.py"
echo ""
echo "To deactivate, run: deactivate"
