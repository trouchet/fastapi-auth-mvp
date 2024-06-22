from fastapi import FastAPI

from backend.app.routes import (
    auth_router, data_router, misc_router,
)

app = FastAPI()

# Include the router in the app
app.include_router(auth_router)
app.include_router(misc_router)
app.include_router(data_router)
