from backend.app.config import settings
from backend.app.database.core import Database
from backend.app.database.initial_data import insert_initial_users

# Load environment variables from the .env file
uri = settings.database_uri()

database = Database(uri)
database.init()

insert_initial_users(database)


def get_session():
    """
    Define a dependency to create a database session

    Returns:
        Database: A NamedTuple with engine and conn attributes for the database connection.
        None: If there was an error connecting to the database.
    """
    return database.session_maker()
