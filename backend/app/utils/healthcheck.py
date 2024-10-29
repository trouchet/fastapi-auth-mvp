from typing import Dict
import psutil
import os
from redis.exceptions import RedisError
from typing import Tuple

from backend.app.database.instance import Database, uri
from backend.app.base.config import settings 

HealthOutputType = Tuple[bool, str]

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
    message_str= '' if is_healthy else error_message

    return {
        "status": status_str,
        "message": message_str,
    }


async def is_server_live() -> HealthOutputType:
    """
    Check if the server is live and running.

    Returns:
        bool: True if the server is live, False otherwise.
    """
    try:
        # Simple check (consider platform-specific methods for robustness)
        return True, ''
    except Exception as e:
        return False, f'Server is not live: {str(e)}'

# Define a default memory threshold (GB)
DEFAULT_MEMORY_THRESHOLD = 1
async def is_memory_usage_within_limits() -> HealthOutputType:
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
            return True, ''

    except Exception as e:
        return False, str(e)


async def is_database_healthy() -> HealthOutputType:
    """
    Check if the database connection is healthy.

    Returns:
        bool: True if the database connection is healthy, False otherwise.
    """
    try:
        database = Database(uri)
        await database.test_connection()
        return True, None
    except Exception as e:
        return False, str(e)

async def is_cache_healthy() -> HealthOutputType:
    """
    Check the health of the Redis cache.

    Args:
        redis_client (aioredis.Redis): The Redis client instance.

    Returns:
        bool: True if the cache is healthy, False otherwise.
    """
    try:
        # Perform a simple ping command to check if Redis is reachable
        result = await settings.redis_client.ping()
        return result, ''
    except Exception as e:
        # Catch any other unexpected exceptions
        return False, f"An unexpected error occurred: {str(e)}"