from backend.app.core.app import app
from backend.app.core.logging import logger

app.logger = logger
app.logger.setLevel("INFO")
app.logger.info("Setting up the application")

