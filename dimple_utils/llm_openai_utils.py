from openai import OpenAI
from dimple_utils import config_utils
from dimple_utils.llm_base import BaseLLM, LLMResponse
import os
import time
import logging
import uuid
from typing import Optional, Dict, Any


class OpenAIClient(BaseLLM):
    """
    A class-based OpenAI client that allows multiple instances with different configurations.
    """
    
    # Class-level constants
    RATE_LIMIT_ERROR_LIST = [
        "Rate limit reached for", 
        "Read timed out", 
        "Connection reset by peer",
        "The server is overloaded or not ready yet"
    ]
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 key_file: Optional[str] = None,
                 model: str = "gpt-4o",
                 retry_delay: int = 60,
                 max_retries: int = 5,
                 max_response_tokens: int = 4096,
                 temperature: float = 0.0,
                 use_config: bool = True):
        """
        Initialize OpenAI client with custom or configuration-based settings.
        
        Args:
            api_key: Direct API key (optional)
            key_file: Path to file containing API key (optional)
            model: OpenAI model to use
            retry_delay: Delay between retries in seconds
            max_retries: Maximum number of retry attempts
            max_response_tokens: Maximum tokens in response
            temperature: Temperature for response generation
            use_config: Whether to load additional settings from config
        """
        # Initialize parent class
        super().__init__(model, retry_delay, max_retries, max_response_tokens, temperature)
        
        self.openai_client = None
        self._config_loaded = False
        
        # Load configuration if requested
        if use_config:
            self._load_from_config()
        
        # Initialize OpenAI client
        self._initialize_openai_client(api_key, key_file)
    
    def _load_from_config(self):
        """Load configuration from config_utils if available."""
        try:
            self.model = config_utils.get_property("openai.model", fallback=self.model)
            self.retry_delay = config_utils.get_int_property("openai.retry.delay", fallback=self.retry_delay)
            self.max_retries = config_utils.get_int_property("openai.max.retries", fallback=self.max_retries)
            self.max_response_tokens = config_utils.get_int_property("openai.max.response_tokens", fallback=self.max_response_tokens)
            self._config_loaded = True
        except Exception as e:
            logging.warning(f"Could not load config, using defaults: {e}")
            self._config_loaded = False
    
    def _initialize_openai_client(self, api_key: Optional[str], key_file: Optional[str]):
        """Initialize OpenAI client from various sources."""
        resolved_api_key = None
        
        # Priority 1: Direct API key parameter
        if api_key:
            resolved_api_key = api_key
            logging.info("Using provided API key")
        
        # Priority 2: Key file parameter
        elif key_file:
            if not os.path.exists(key_file):
                raise FileNotFoundError(f"OpenAI key file not found: {os.path.abspath(key_file)}")
            
            with open(key_file, 'r') as f:
                resolved_api_key = f.read().strip()
            logging.info(f"Using API key from file: {key_file}")
        
        # Priority 3: Environment variable
        elif os.getenv("OPENAI_API_KEY"):
            resolved_api_key = os.getenv("OPENAI_API_KEY")
            logging.info("Using API key from environment variable OPENAI_API_KEY")
        
        # Priority 4: Config file (if use_config=True)
        elif hasattr(self, '_config_loaded') and self._config_loaded:
            try:
                config_key_file = config_utils.get_property("openai.key.file", fallback="openai_key_dont_commit.txt")
                if os.path.exists(config_key_file):
                    with open(config_key_file, 'r') as f:
                        resolved_api_key = f.read().strip()
                    logging.info(f"Using API key from config file: {config_key_file}")
            except Exception as e:
                logging.warning(f"Could not load API key from config: {e}")
        
        # Initialize client if we have a key
        if resolved_api_key:
            self.openai_client = OpenAI(api_key=resolved_api_key)
            self._initialized = True
            logging.info(f"OpenAI client initialized successfully. Model: {self.model}")
        else:
            raise ValueError("No API key found. Provide api_key, key_file, or set OPENAI_API_KEY environment variable.")
    
    def initialize(self) -> None:
        """Initialize the OpenAI client (already done in __init__)."""
        if not self._initialized:
            raise RuntimeError("OpenAI client not initialized. Check API key configuration.")
    
    def _infer_query(self, 
                    prompt: str,
                    model: str,
                    temperature: float,
                    max_tokens: int,
                    response_format: Optional[Dict[str, Any]] = None,
                    log_msg: str = "") -> LLMResponse:
        """
        OpenAI-specific inference implementation.
        
        Args:
            prompt: The input prompt
            model: The model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            response_format: Optional response format specification
            log_msg: Additional log message
            
        Returns:
            LLMResponse containing text_reply, input_tokens, output_tokens, and time_taken_ms
        """
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract token usage information
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        
        return LLMResponse(
            text_reply=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            time_taken_ms=0  # Will be set by the base class
        )
    
    
# Legacy function-based interface for backward compatibility
def initialize():
    """Legacy function for backward compatibility. Creates a global instance."""
    global _global_client
    _global_client = OpenAIClient()
    logging.info("Global OpenAI client initialized for backward compatibility")


def infer_query(prompt, response_format=None, log_msg=""):
    """Legacy function for backward compatibility."""
    global _global_client
    if _global_client is None:
        initialize()
    return _global_client.infer_query(prompt, response_format, log_msg)


# Global client for backward compatibility
_global_client = None
