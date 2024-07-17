from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.app.base.logging import logger

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Counter for dummy task
execution_count = 0

async def dummy_task():
    global execution_count
    execution_count += 1

    if execution_count % 3 == 0:
        raise Exception("Intentional failure for testing")

    logger.info("TEsting task executed successfully")