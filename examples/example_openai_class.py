#!/usr/bin/env python3
"""
Example demonstrating how to use the new OpenAIClient class.

This example shows how to create multiple instances with different configurations
and use them independently.

To run this script:
1. cd to the dimple_utils directory
2. Run: source activate_venv.sh
3. Run: python examples/example_openai_class.py
"""

import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import dimple_utils
# This is needed when running from the examples directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from dimple_utils.llm_openai_utils import OpenAIClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the dimple_utils directory with the virtual environment activated.")
    print("Run: source activate_venv.sh")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Demonstrate different ways to use the OpenAIClient class."""
    
    print("=== OpenAI Client Class Examples ===\n")
    
    client1 = None
    try:
        # Note: In practice, you'd get this from environment or secure storage
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client1 = OpenAIClient(
                api_key=api_key,
                model="gpt-4o",
                max_response_tokens=4096,
                temperature=0.0
            )
            print(f"Client 1 created: {client1.get_model_info()}")
        else:
            print("No OPENAI_API_KEY found in environment")
            print("Set OPENAI_API_KEY environment variable to run this example")
    except Exception as e:
        print(f"Error creating client 1: {e}")
    
    print("\nExample inference usage...")
    if client1:
        response = client1.infer_query(
            prompt="Who was the first president of the United States?",
            log_msg="Test query"
        )
        print(f"Response: {response.text_reply}")
        print(f"Input tokens: {response.input_tokens}")
        print(f"Output tokens: {response.output_tokens}")
        print(f"Time taken: {response.time_taken_ms}ms")
    else:
        print("No valid client available for inference")
    
    print("\n=== Examples Complete ===")

if __name__ == "__main__":
    main()
