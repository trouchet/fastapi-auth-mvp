from backend.app.config import settings
from backend.app.database.core import Database
from backend.app.database.initial_data import insert_initial_users

# Load environment variables from the .env file
uri = settings.database_uri()

# Create a database connection
database = Database(uri)
database.init()

# Insert first user
insert_initial_users(database)


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
