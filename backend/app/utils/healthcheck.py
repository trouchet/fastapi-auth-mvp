from typing import Dict
import psutil
import os

from backend.app.database.instance import database

def healthcheck_dict(is_healthy: bool, error_message: str) -> Dict:
    """
    Returns a dictionary representing the health check status.

    Args:
        is_healthy (bool): Indicates whether the service is healthy or not.
        error_message (str): The error message to include if the service is not healthy.

    Returns:
        dict: A dictionary with the following keys:
            - "status": The status of the health check, either "healthy" or "warning".
            - "message": The error message if the service is not healthy, otherwise an empty string.
    """
    status_str = 'healthy' if is_healthy else 'warning'
    
    return {
        "status": status_str,
        "message": error_message if not is_healthy else '',
    }


async def is_server_live() -> bool:
    """
    Check if the server is live and running.

    Returns:
        bool: True if the server is live, False otherwise.
    """
    try:
        # Simple check (consider platform-specific methods for robustness)
        import backend.app.main as main
        return True, ''
    except Exception as e:
        return False, f'Server is not live: {str(e)}'

# Define a default memory threshold (GB)
DEFAULT_MEMORY_THRESHOLD = 1
async def is_memory_usage_within_limits() -> bool:
    """
    Check if the memory usage is within the defined limits.

    Returns:
        bool: True if the memory usage is within limits, False otherwise.
        str: A message indicating the reason if the memory usage exceeds the threshold, None otherwise.
    """
    try:
        # Get current process object
        process = psutil.Process(os.getpid())

        # Check memory usage
        memory_usage = process.memory_info().rss / (1024 * 1024 * 1024)  # Convert to GB

        # Check if memory usage exceeds 1 GB
        if memory_usage > DEFAULT_MEMORY_THRESHOLD:
            usage = f"{memory_usage:.2f} GB"
            threshold = f"{DEFAULT_MEMORY_THRESHOLD} GB"
            return False, f"Memory usage ({usage}) exceeds threshold ({threshold})"
        else:
            return True, None

    except Exception:
        return False


async def is_database_healthy() -> bool:
    """
    Check if the database connection is healthy.

    Returns:
        bool: True if the database connection is healthy, False otherwise.
    """
    try:
        database.test_connection()
        return True, None
    except Exception as e:
        return False, str(e)

async def is_cache_healthy() -> bool:
    """
    Check the health of the cache.

    Returns:
        bool: True if the cache is healthy, False otherwise.
    """
    try:
        raise NotImplementedError("Cache health check not implemented")
    except Exception as e:
        return False, str(e)