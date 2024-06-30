from backend.app.core.config import settings
from backend.app.database.core import Database

# Load environment variables from the .env file
is_testing = settings.ENVIRONMENT == "testing"
uri = settings.database_uri if not is_testing else settings.test_database_uri

# Create a database connection
database = Database(uri)
database.init()

def get_session():
    """
    Define a dependency to create a database session

    Returns:
        Database: A NamedTuple with engine and conn attributes for the database connection.
        None: If there was an error connecting to the database.
    """
    
    session = database.session_maker()
    try:
        return session
    finally:
        session.close()
