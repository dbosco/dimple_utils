#!/usr/bin/env python3
"""
Example script demonstrating the AnthropicClient class usage.
This shows how to create and use multiple Anthropic client instances.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import dimple_utils
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from dimple_utils import AnthropicClient

def main():
    """Demonstrate AnthropicClient usage."""
    print("=== Anthropic Client Class Examples ===\n")
    
    # Example 1: Create client with API key from environment
    try:
        # Get API key from environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            client = AnthropicClient(api_key=api_key)
            print(f"Client 1 created: {client.get_model_info()}")
            
            # Example inference usage
            print("\nExample inference usage...")
            response = client.infer_query(
                prompt="Who was the first president of the United States?",
                log_msg="Test query"
            )
            print(f"Response: {response}")
        else:
            print("No ANTHROPIC_API_KEY found in environment")
            print("Set ANTHROPIC_API_KEY environment variable to run this example")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable or provide api_key parameter")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n=== Examples Complete ===")

if __name__ == "__main__":
    main()
