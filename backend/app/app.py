from fastapi import FastAPI

from backend.app.routes import router

app = FastAPI()

# Include the router in the app
app.include_router(router)