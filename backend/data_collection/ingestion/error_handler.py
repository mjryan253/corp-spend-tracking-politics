"""
Error handling utilities with exponential backoff for API requests.
"""
import time
import random
import logging
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import requests


logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(APIError):
    """Exception for rate limit errors."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ExponentialBackoff:
    """
    Implements exponential backoff with jitter for retrying failed operations.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize exponential backoff.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number."""
        if attempt <= 0:
            return 0
        
        # Calculate exponential delay
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        
        # Cap at maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to avoid thundering herd problem
        if self.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to add exponential backoff to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == self.max_retries:
                        break
                    
                    # Check if this is a retryable error
                    if not self._is_retryable_error(e):
                        break
                    
                    # Calculate delay and wait
                    delay = self.calculate_delay(attempt + 1)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Handle rate limit specific delays
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = max(delay, e.retry_after)
                        logger.info(f"Rate limited. Waiting {delay} seconds as suggested by API.")
                    
                    time.sleep(delay)
            
            # If we get here, all retries failed
            logger.error(f"All {self.max_retries + 1} attempts failed. Last error: {str(last_exception)}")
            raise last_exception
        
        return wrapper
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        # Network errors are generally retryable
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True
        
        # API errors with specific status codes
        if isinstance(error, requests.HTTPError):
            # 5xx server errors are retryable
            if 500 <= error.response.status_code < 600:
                return True
            
            # 429 Too Many Requests is retryable
            if error.response.status_code == 429:
                return True
            
            # 408 Request Timeout is retryable
            if error.response.status_code == 408:
                return True
        
        # Custom API errors
        if isinstance(error, RateLimitError):
            return True
        
        if isinstance(error, APIError):
            # Retry on server errors
            if error.status_code and 500 <= error.status_code < 600:
                return True
            # Retry on rate limits
            if error.status_code == 429:
                return True
        
        # Don't retry client errors (4xx except 408, 429)
        return False


def robust_api_request(
    url: str,
    method: str = 'GET',
    headers: Optional[Dict] = None,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 30,
    max_retries: int = 3
) -> requests.Response:
    """
    Make a robust API request with error handling and retries.
    
    Args:
        url: Request URL
        method: HTTP method
        headers: Request headers
        params: Query parameters
        json_data: JSON request body
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
    
    Returns:
        Response object
    
    Raises:
        APIError: For API-related errors
        RateLimitError: For rate limiting errors
    """
    backoff = ExponentialBackoff(max_retries=max_retries)
    
    @backoff
    def _make_request():
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = None
                if 'Retry-After' in response.headers:
                    try:
                        retry_after = int(response.headers['Retry-After'])
                    except ValueError:
                        pass
                
                raise RateLimitError(
                    f"Rate limited by API: {response.text}",
                    retry_after=retry_after
                )
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout after {timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            raise APIError(f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            response = e.response
            error_data = None
            try:
                error_data = response.json()
            except:
                pass
            
            raise APIError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
                response_data=error_data
            )
    
    return _make_request()


def log_api_metrics(func: Callable) -> Callable:
    """Decorator to log API call metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_msg = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            log_level = logging.INFO if success else logging.ERROR
            status = "SUCCESS" if success else "FAILED"
            
            logger.log(
                log_level,
                f"API call {func.__name__}: {status} in {duration:.2f}s"
                + (f" - Error: {error_msg}" if error_msg else "")
            )
    
    return wrapper


class APICallCounter:
    """Track API call statistics."""
    
    def __init__(self):
        self.calls = {}
        self.errors = {}
    
    def record_call(self, api_name: str, success: bool = True):
        """Record an API call."""
        if api_name not in self.calls:
            self.calls[api_name] = {"total": 0, "success": 0, "failed": 0}
        
        self.calls[api_name]["total"] += 1
        if success:
            self.calls[api_name]["success"] += 1
        else:
            self.calls[api_name]["failed"] += 1
    
    def record_error(self, api_name: str, error_type: str):
        """Record an API error."""
        if api_name not in self.errors:
            self.errors[api_name] = {}
        
        if error_type not in self.errors[api_name]:
            self.errors[api_name][error_type] = 0
        
        self.errors[api_name][error_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API call statistics."""
        return {
            "calls": self.calls,
            "errors": self.errors,
            "total_calls": sum(stats["total"] for stats in self.calls.values()),
            "total_errors": sum(stats["failed"] for stats in self.calls.values())
        }
    
    def reset(self):
        """Reset all statistics."""
        self.calls.clear()
        self.errors.clear()


# Global API call counter
api_counter = APICallCounter()


def track_api_calls(api_name: str):
    """Decorator to track API calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                api_counter.record_call(api_name, success=True)
                return result
            except Exception as e:
                api_counter.record_call(api_name, success=False)
                api_counter.record_error(api_name, type(e).__name__)
                raise
        return wrapper
    return decorator


# Convenience decorators with common settings
retry_on_failure = ExponentialBackoff(max_retries=3, base_delay=1.0)
aggressive_retry = ExponentialBackoff(max_retries=5, base_delay=0.5, max_delay=30.0)
conservative_retry = ExponentialBackoff(max_retries=2, base_delay=2.0, max_delay=10.0)


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """
    Circuit breaker pattern implementation.
    
    Prevents cascade failures by stopping calls to a failing service
    after a threshold of failures is reached.
    """
    def decorator(func: Callable) -> Callable:
        state = {"failures": 0, "last_failure_time": 0, "is_open": False}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Check if circuit should reset (recovery timeout passed)
            if (state["is_open"] and 
                current_time - state["last_failure_time"] > recovery_timeout):
                state["is_open"] = False
                state["failures"] = 0
                logger.info(f"Circuit breaker for {func.__name__} reset after recovery timeout")
            
            # If circuit is open, fail fast
            if state["is_open"]:
                raise APIError(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Service is temporarily unavailable."
                )
            
            try:
                result = func(*args, **kwargs)
                # Reset failure count on success
                state["failures"] = 0
                return result
                
            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = current_time
                
                # Open circuit if failure threshold reached
                if state["failures"] >= failure_threshold:
                    state["is_open"] = True
                    logger.error(
                        f"Circuit breaker OPENED for {func.__name__} "
                        f"after {failure_threshold} failures"
                    )
                
                raise
        
        return wrapper
    return decorator
