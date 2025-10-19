from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging


class BaseLLM(ABC):
    """
    Base class for LLM providers that defines the common interface.
    """
    
    def __init__(self, 
                 model: str,
                 retry_delay: int = 60,
                 max_retries: int = 5,
                 max_response_tokens: int = 4096,
                 temperature: float = 0.0):
        """
        Initialize the base LLM client.
        
        Args:
            model: The model name to use
            retry_delay: Delay between retries in seconds
            max_retries: Maximum number of retry attempts
            max_response_tokens: Maximum tokens in response
            temperature: Temperature for response generation
        """
        self.model = model
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.max_response_tokens = max_response_tokens
        self.temperature = temperature
        self._initialized = False
    
    def infer_query(self, 
                   prompt: str, 
                   response_format: Optional[Dict[str, Any]] = None, 
                   log_msg: str = "",
                   model: Optional[str] = None,
                   temperature: Optional[float] = None,
                   max_tokens: Optional[int] = None,
                   max_retries: Optional[int] = None) -> str:
        """
        Execute inference query with the configured LLM client.
        This is the public interface that handles common logic including retry.
        
        Args:
            prompt: The input prompt
            response_format: Optional response format specification
            log_msg: Additional log message
            model: Override the default model for this request
            temperature: Override the default temperature for this request
            max_tokens: Override the default max tokens for this request
            max_retries: Override the default max retries for this request
            
        Returns:
            The response text from the LLM
        """
        if not self._initialized:
            raise RuntimeError("LLM client not initialized. Call initialize() first.")
        
        # Use parameter values or fall back to instance defaults
        actual_model = model or self.model
        actual_temperature = temperature if temperature is not None else self.temperature
        actual_max_tokens = max_tokens or self.max_response_tokens
        actual_max_retries = max_retries if max_retries is not None else self.max_retries
        
        # Use retry logic to call the provider-specific implementation
        def _make_inference_request():
            return self._infer_query(
                prompt=prompt,
                model=actual_model,
                temperature=actual_temperature,
                max_tokens=actual_max_tokens,
                response_format=response_format,
                log_msg=log_msg
            )
        
        return self._handle_retry_logic("LLM inference", _make_inference_request, actual_max_retries)
    
    @abstractmethod
    def _infer_query(self, 
                    prompt: str,
                    model: str,
                    temperature: float,
                    max_tokens: int,
                    response_format: Optional[Dict[str, Any]] = None,
                    log_msg: str = "") -> str:
        """
        Provider-specific inference implementation.
        Must be implemented by subclasses.
        
        Args:
            prompt: The input prompt
            model: The model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            response_format: Optional response format specification
            log_msg: Additional log message
            
        Returns:
            The response text from the LLM
        """
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the LLM client.
        Must be implemented by subclasses.
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration information."""
        return {
            "model": self.model,
            "retry_delay": self.retry_delay,
            "max_retries": self.max_retries,
            "max_response_tokens": self.max_response_tokens,
            "temperature": self.temperature,
            "initialized": self._initialized
        }
    
    def _handle_retry_logic(self, 
                          operation_name: str,
                          operation_func,
                          max_retries: Optional[int] = None,
                          *args, 
                          **kwargs) -> Any:
        """
        Common retry logic for LLM operations.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            max_retries: Override the default max retries for this operation
            *args: Arguments for the operation function
            **kwargs: Keyword arguments for the operation function
            
        Returns:
            Result of the operation function
        """
        retries = max_retries if max_retries is not None else self.max_retries
        
        for attempt in range(retries):
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                if self._is_retryable_error(e) and attempt < retries - 1:
                    logging.warning(f"Failed to execute {operation_name}. Attempt= {attempt + 1}/{retries}. "
                                   f"We will retry after {self.retry_delay} seconds. exception={e}")
                    import time
                    time.sleep(self.retry_delay)
                    continue
                else:
                    if self._is_retryable_error(e):
                        raise Exception(f"Failed to execute {operation_name} after {retries} attempts.") from e
                    raise
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Check if an error is retryable.
        Can be overridden by subclasses for provider-specific error handling.
        
        Args:
            error: The exception to check
            
        Returns:
            True if the error is retryable, False otherwise
        """
        # Default implementation - can be overridden by subclasses
        retryable_errors = [
            "Rate limit reached for",
            "Read timed out", 
            "Connection reset by peer",
            "The server is overloaded or not ready yet"
        ]
        return any(msg in str(error) for msg in retryable_errors)
