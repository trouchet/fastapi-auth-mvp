from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker


from backend.app.core.logging import logger
from backend.app.database.models.base import Base
from backend.app.utils.misc import try_do


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

    def create_database(self):
        # Create the database if it does not exist
        def create_database_alias():
            if not database_exists(self.uri):
                # Create the database engine and session maker
                create_database(self.uri)

        try_do(create_database_alias, "creating database")

    def test_connection(self):
        def test_connection():
            with self.engine.connect() as conn:
                query = text("SELECT 1")

                # Test the connection
                conn.execute(query)

                logger.info("Connection to the database established!")

        try_do(test_connection, "testing connection")

    def create_tables(self):
        """
        Connects to a PostgreSQL database using environment variables for connection details.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.

        """

        def create_tables_alias():
            Base.metadata.create_all(self.engine)
            
            # print available tables
            logger.info("Tables created:")
            for table in Base.metadata.tables:
                logger.info(f"Table: {table}")
            

        try_do(create_tables_alias, "creating tables")

    def init(self):
        """
        Initializes the database connection and creates the tables.

        Args:
            uri (str): The database URI.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.
        """

        self.create_database()
        self.test_connection()
        self.create_tables()
