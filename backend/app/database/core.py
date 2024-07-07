from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.exc import OperationalError
from asyncio import current_task 

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
        self.engine = create_async_engine(
            uri,
            future=True,               # Use the new asyncio-based execution strategy
            pool_size=20,              # Adjust pool size based on your workload
            max_overflow=10,           # Adjust maximum overflow connections
            pool_recycle=3600,         # Periodically recycle connections (optional)
            pool_pre_ping=True,        # Check the connection status before using it
        )
        self.session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.scoped_session_maker = async_scoped_session(
            self.session_maker, scopefunc=current_task
        )

    async def database_exists(self, uri):
        """
        Checks if the database exists for the given URI.

        Args:
            uri: The database connection URI string.

        Returns:
            True if the database exists, False otherwise.
        """
        engine = create_async_engine(uri, echo=False)  # Create engine without echo
        try:
            await engine.connect()
            await engine.execute(text("SELECT 1"))  # Execute a simple query
            return True
        except Exception:
            return False
        finally:
            await engine.dispose()  # Close the engine connection

    
    async def create_database(self):
        # Split the URI to get the database name
        database_name = self.uri.split("/")[-1]
        uri_without_database = '/'.join(self.uri.split("/")[:-1])

        print(database_name)
        print(uri_without_database)

        try:
            # Create a new engine without specifying a database
            engine = create_async_engine(
                uri_without_database,
                future=True,               # Use the new asyncio-based execution strategy
                pool_size=20,              # Adjust pool size based on your workload
                max_overflow=10,           # Adjust maximum overflow connections
                pool_recycle=3600,         # Periodically recycle connections (optional)
                pool_pre_ping=True,        # Check the connection status before using it
            )

            # Create a new connection to execute the CREATE DATABASE statement
            async with engine.begin() as conn:
                
                    print(f'{database_name}')
                    await conn.execute(text("COMMIT"))
                    await conn.execute(text(f"CREATE DATABASE {database_name}"))
                    logger.info(f"Database '{database_name}' created successfully.")
        except Exception as e:
            logger.error(f"Error creating database '{database_name}': {e}")


    async def test_connection(self):
        try:
            async with self.engine.connect() as conn:
                query = text("SELECT 1")

                # Test the connection
                await conn.execute(query)

                logger.info("Connection to the database established!")
        except Exception as e:
            logger.error(f"Error connecting to the database: {str(e)}")
            

    async def create_tables(self):
        """
        Connects to a PostgreSQL database using environment variables for connection details.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.

        """

        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Print available tables
            for table in Base.metadata.tables:
                logger.info(f"Table created: {table}")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
                

    def get_tables(self, conn: AsyncSession):
        inspector = inspect(conn)
        return inspector.get_table_names()

    async def print_tables(self):
        """
        Print the available tables in the database.
        """
        try:
            async with self.engine.connect() as conn:
                # Use a synchronous context to run the inspector
                result = await conn.run_sync(self.get_tables)
                logger.info(f"Available tables: {result}")
        except Exception as e:
            logger.error(f"Error fetching table names: {str(e)}")


    async def init(self):
        """
        Initializes the database connection and creates the tables.

        Args:
            uri (str): The database URI.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.
        """
        if(not await self.database_exists(self.uri)):
            await self.create_database()
        else:
            logger.warning("Database already exists!")
        
        await self.test_connection()
        await self.create_tables()
        await self.print_tables()

