from os import getenv, path, getcwd
from dotenv import load_dotenv
from psycopg2 import OperationalError
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import pool, text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from backend.logging import logger
from backend.database.schemas import Base

Base = declarative_base()


def get_db_uri():
    env_path = path.join(getcwd(), ".env")
    load_dotenv(env_path)

    # Get environment variables
    host = getenv("POSTGRES_HOST", "localhost")
    port = int(getenv("POSTGRES_PORT", "5432"))
    user = getenv("POSTGRES_USER", "postgres")
    passw = getenv("POSTGRES_PASSWORD", "postgres")
    database_name = getenv("POSTGRES_DBNAME")

    # Connect to the database
    return f"postgresql://{user}:{passw}@{host}:{port}/{database_name}"


class Database:
    """
    This class represents a database connection and session management object.
    It contains two attributes:

    - engine: A callable that represents the database engine.
    - session_maker: A callable that represents the session maker.
    """

    def __init__(self, uri):
        self.uri = uri
        self.engine = create_engine(
            uri,
            poolclass=pool.QueuePool,  # Use connection pooling
            pool_size=20,  # Adjust pool size based on your workload
            max_overflow=10,  # Adjust maximum overflow connections
            pool_recycle=3600,  # Periodically recycle connections (optional)
        )
        self.session_maker = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self):
        yield self.session_maker()

    def create_database(self):
        # Create the database if it does not exist
        try:
            if not database_exists(self.uri):
                # Create the database engine and session maker
                create_database(self.uri)

        except OperationalError as e:
            logger.error(f"Error creating to database: {e}")

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                query = text("SELECT 1")

                # Test the connection
                conn.execute(query)

                logger.info("Connection to the database established!")

        except OperationalError as e:
            logger.error(f"Error connecting to the database: {e}")

    def create_tables(self):
        """
        Connects to a PostgreSQL database using environment variables for connection details.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.

        """
        try:
            # Create all tables defined using the Base class (if not already created)
            Base.metadata.create_all(self.engine)

        except Exception as e:
            logger.error(f"Error creating tables in the database: {str(e)}")

    def init(self):
        """
        Initializes the database connection and creates the tables.

        Args:
            uri (str): The database URI.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.
        """

        try:
            self.create_database()
        except Exception as e:
            logger.error(f"Error creating database: {e}")

        try:
            self.test_connection()
        except Exception as e:
            logger.error(f"Error testing connection: {e}")

        try:
            self.create_tables()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")


async def get_db():
    """
    Define a dependency to create a database connection

    Returns:
        Database: A NamedTuple with engine and conn attributes for the database connection.
        None: If there was an error connecting to the database.
    """

    uri = get_db_uri()

    if uri is None:
        # Handle the case where URI is not available (raise exception, log error, etc.)
        error_message = f"Database URI {uri} not found"
        logger.error(error_message)
        raise Exception(error_message)

    database = Database(uri)
    database.init()

    yield database
