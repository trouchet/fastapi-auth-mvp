from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.database.core import Database

# Load environment variables from the .env file
is_testing = settings.ENVIRONMENT == "testing"
uri = settings.database_uri if not is_testing else settings.test_database_uri

database = None

# Global variable to hold the database instance
# Function to create and initialize the database
async def init_database():
    global database
    database = Database(uri)
    await database.init()


@asynccontextmanager
async def get_session():
    """
    Define a dependency to create a database session asynchronously.

    Returns:
        Database: A NamedTuple with engine and conn attributes for the database connection.
        None: If there was an error connecting to the database.
    """
    # Ensure database is initialized before getting a session
    if database is None:
        await init_database()
    
    async with database.session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
