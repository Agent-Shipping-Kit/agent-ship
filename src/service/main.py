'''
This is the main file for the backend.
'''
import logging
import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from src.agents.registry import discover_agents
from src.service.routers.rest_router import router as rest_router
load_dotenv()

# logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HealthLogue Agents API",
    description="This is the agents API for the HealthLogue AI Agents.",
    version="1.0.0",
    contact={
        "name": "HealthLogue Support",
        "email": "support@healthlogue.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.get("/")
async def read_root():
    '''
    Root endpoint for the backend.
    '''
    logger.info("Root endpoint hit")
    return {"message": "Welcome to the HealthLogue AI Api!"}


@app.get("/health")
async def health_check():
    '''
    Health check endpoint for the backend.
    '''
    return {"status": "running"}

# Ensure agents are discovered (idempotent)
discover_agents("src/agents/all_agents")

app.include_router(rest_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
