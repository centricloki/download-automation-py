"""
Utility functions for the download automation framework.

This module provides helper functions for:
- Directory creation and management
- File waiting and validation
- Retry logic with exponential backoff
- Common async operations

All functions are designed to be async-compatible for use with asyncio.
"""

import asyncio
from pathlib import Path
import time
import logging
from typing import Optional, Callable, Any


async def ensure_dir(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary (including parent directories).
    
    Args:
        path: Directory path to create/ensure
        
    Example:
        >>> await ensure_dir("downloads/my_site")
        # Creates 'downloads' and 'my_site' if they don't exist
    """
    Path(path).mkdir(parents=True, exist_ok=True)


async def wait_for_file(
    download_dir: str, 
    timeout: int = 180, 
    pattern: str = "*.xlsx"
) -> str:
    """
    Wait for a file matching the pattern to appear in the download directory.
    
    Uses polling to check for file existence every 2 seconds.
    Returns the most recently created file matching the pattern.
    
    Args:
        download_dir: Directory where file is expected to be downloaded
        timeout: Maximum wait time in seconds (default: 180)
        pattern: Glob pattern to match files (default: "*.xlsx")
        
    Returns:
        str: Full path to the latest file matching the pattern
        
    Raises:
        TimeoutError: If no file found within timeout period
        
    Example:
        >>> file_path = await wait_for_file("downloads/delaware", timeout=120, pattern="*.xlsx")
        >>> print(f"Found file: {file_path}")
    """
    end_time = time.time() + timeout
    
    while time.time() < end_time:
        # Find all files matching the pattern
        files = list(Path(download_dir).glob(pattern))
        
        if files:
            # Get the most recently created file
            latest = max(files, key=lambda f: f.stat().st_ctime)
            return str(latest)
        
        # Poll every 2 seconds
        await asyncio.sleep(2)
    
    # Timeout reached without finding file
    raise TimeoutError(f"No file matching '{pattern}' found in {download_dir} within {timeout}s")


async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    """
    Execute an async function with exponential backoff retry logic.
    
    Retries the function call if it raises an exception, increasing delay
    between retries exponentially: base_delay * (backoff_factor ^ attempt)
    
    Args:
        func: Async function to execute
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 60.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result from successful function execution
        
    Raises:
        Exception: Last exception if all retries fail
        
    Example:
        >>> result = await retry_with_backoff(
        ...     download_function, 
        ...     url="https://example.com",
        ...     max_retries=5,
        ...     base_delay=2.0
        ... )
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            # Attempt to execute the function
            return await func(*args, **kwargs)
            
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                
                logging.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                # Wait before next retry
                await asyncio.sleep(delay)
            else:
                # Final attempt failed
                logging.error(f"All {max_retries} attempts failed. Last error: {e}")
    
    # Re-raise the last exception if we get here
    raise last_exception
