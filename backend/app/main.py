from .app import app
from backend.app.base.logging import logger

app.logger = logger
app.logger.setLevel("INFO")
app.logger.info("Setting up the application")

