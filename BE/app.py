import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.rooms import router as rooms_router
from routers.heartbeat import router as heartbeat
from routers.websocket_manager import router as websocket_router

# Define the URLs you want to accept cross-origin requests from.
origins = [
    'https://scrumpoker-c686f.web.app'
]


# Configure logging to output at the INFO level
logging.basicConfig(level=logging.INFO)

# Instantiate the FastAPI application
app = FastAPI()

# Include the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the WebSocket router
app.include_router(websocket_router)
app.include_router(heartbeat)
app.include_router(rooms_router)
