import datetime
import logging
import sys
from os import getenv
from datetime import datetime
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

from backend.app.utils.logging import DailyHierarchicalFileHandler

# Use the logger
logger = logging.getLogger(__name__)

# Configure logging with a single handler
# Set the overall logging level
load_dotenv()
ENVIRONMENT = getenv("ENVIRONMENT", "development")

fields = [
    "name", "process","processName","threadName","thread","taskName",
    "asctime","created","relativeCreated","msecs",
    "pathname", "module","filename","funcName","levelno","levelname", "message",
]

field_map=lambda field_name: f"%({field_name})s"
logging_format = " ".join(map(field_map, fields))
formatter = jsonlogger.JsonFormatter(logging_format)

if ENVIRONMENT == "development":
    # Create a handler for stdout and stderr
    stdout_stream_handler = logging.StreamHandler(sys.stdout)
    stderr_stream_handler = logging.StreamHandler(sys.stderr)

    # Set the format for the handlers
    stdout_stream_handler.setFormatter(formatter)
    stderr_stream_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[stdout_stream_handler])
    logging.basicConfig(level=logging.WARN, handlers=[stderr_stream_handler])


# Create daily rotating file handler with hierarchy
handler = DailyHierarchicalFileHandler("logs/my_app.log", when="midnight")
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("Logging started.")

