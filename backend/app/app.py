from fastapi import FastAPI
from routes import router

app = FastAPI()

# Include the router in the app
app.include_router(router)