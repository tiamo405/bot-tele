"""
Retry decorator for API calls and network operations
"""
import time
import functools
from typing import Callable, Any, Tuple, Type
import logging

logger = logging.getLogger(__name__)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_errors: bool = True
):
    """
    Decorator để retry function khi gặp exception
    
    Args:
        max_retries: Số lần retry tối đa
        delay: Thời gian delay ban đầu (giây)
        backoff: Hệ số nhân delay sau mỗi lần retry
        exceptions: Tuple các exception cần retry
        log_errors: Có log lỗi hay không
    
    Examples:
        @retry_on_exception(max_retries=3, delay=1.0)
        def fetch_data():
            # Code có thể fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        if log_errors:
                            logger.error(
                                f"Function {func.__name__} failed after {max_retries} retries: {e}"
                            )
                        raise
                    
                    if log_errors:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Shouldn't reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_with_timeout(
    max_retries: int = 3,
    timeout: float = 10.0,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator để retry với timeout cho mỗi attempt
    
    Args:
        max_retries: Số lần retry tối đa
        timeout: Timeout cho mỗi lần thử (giây)
        delay: Delay giữa các lần retry
        exceptions: Tuple các exception cần retry
    
    Note:
        Requires concurrent.futures for timeout functionality
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError
            
            for attempt in range(max_retries + 1):
                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        return future.result(timeout=timeout)
                        
                except TimeoutError:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} timeout after {max_retries} retries")
                        raise
                    logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}. Retrying...")
                    time.sleep(delay)
                    
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay)
        
        return wrapper
    return decorator
