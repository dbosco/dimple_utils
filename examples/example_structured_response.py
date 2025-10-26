#!/usr/bin/env python3
"""
Example demonstrating the new structured response format.

This example shows how the LLM clients now return structured responses
with text_reply, input_tokens, output_tokens, and time_taken_ms.
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

from dimple_utils.llm_base import LLMResponse
from dimple_utils.llm_openai_utils import OpenAIClient
from dimple_utils.llm_anthropic_utils import AnthropicClient

def demonstrate_structured_response():
    """Demonstrate the new structured response format."""
    print("=== Structured Response Example ===\n")
    
    # Example 1: Create a mock response to show the structure
    mock_response = LLMResponse(
        text_reply="This is a sample response from the LLM.",
        input_tokens=25,
        output_tokens=8,
        time_taken_ms=1250
    )
    
    print("Mock LLMResponse structure:")
    print(f"  text_reply: '{mock_response.text_reply}'")
    print(f"  input_tokens: {mock_response.input_tokens}")
    print(f"  output_tokens: {mock_response.output_tokens}")
    print(f"  time_taken_ms: {mock_response.time_taken_ms}")
    print()
    
    # Example 2: Try with OpenAI if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            print("Testing with OpenAI...")
            client = OpenAIClient(api_key=openai_key)
            response = client.infer_query(
                prompt="Say 'Hello, structured response!' in exactly those words.",
                log_msg="Structured response test"
            )
            
            print("OpenAI Response:")
            print(f"  text_reply: '{response.text_reply}'")
            print(f"  input_tokens: {response.input_tokens}")
            print(f"  output_tokens: {response.output_tokens}")
            print(f"  time_taken_ms: {response.time_taken_ms}ms")
            print()
        except Exception as e:
            print(f"OpenAI test failed: {e}")
            print()
    
    # Example 3: Try with Anthropic if API key is available
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            print("Testing with Anthropic...")
            client = AnthropicClient(api_key=anthropic_key)
            response = client.infer_query(
                prompt="Say 'Hello, structured response!' in exactly those words.",
                log_msg="Structured response test"
            )
            
            print("Anthropic Response:")
            print(f"  text_reply: '{response.text_reply}'")
            print(f"  input_tokens: {response.input_tokens}")
            print(f"  output_tokens: {response.output_tokens}")
            print(f"  time_taken_ms: {response.time_taken_ms}ms")
            print()
        except Exception as e:
            print(f"Anthropic test failed: {e}")
            print()
    
    if not openai_key and not anthropic_key:
        print("No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY to test with real APIs.")
        print("The mock response above shows the structure of the new LLMResponse format.")
    
    print("=== Example Complete ===")

if __name__ == "__main__":
    demonstrate_structured_response()
