'''
This is the main file for the backend.
'''
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from src.agents.registry import discover_agents
from src.service.routers.rest_router import router as rest_router
load_dotenv()

# logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgentShip API",
    description="AgentShip - An Agent Shipping Kit. Production-ready AI Agent framework with multiple agent patterns and observability.",
    version="1.0.0",
    contact={
        "name": "AgentShip Support",
        "email": "support@agentship.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/swagger",  # Swagger UI at /swagger
    redoc_url="/redoc",   # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI JSON at /openapi.json
)

@app.get("/")
async def read_root():
    '''
    Root endpoint for the backend.
    '''
    logger.info("Root endpoint hit")
    return {"message": "Welcome to the AgentShip API!"}


@app.get("/health")
async def health_check():
    '''
    Health check endpoint for the backend.
    '''
    return {"status": "running"}

# Serve MkDocs documentation at /docs
# Check if docs site exists, otherwise redirect to GitHub Pages
docs_site_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "site")
if os.path.exists(docs_site_path) and os.path.exists(os.path.join(docs_site_path, "index.html")):
    # Mount static files for MkDocs site
    app.mount("/docs", StaticFiles(directory=docs_site_path, html=True), name="docs")
else:
    # If docs not built, redirect to GitHub Pages (update URL when deploying)
    @app.get("/docs")
    @app.get("/docs/{path:path}")
    async def docs_redirect(path: str = ""):
        """Redirect to framework documentation."""
        docs_url = "https://yourusername.github.io/agentship/"
        if path:
            docs_url = f"{docs_url}{path}"
        return RedirectResponse(url=docs_url)

# Ensure agents are discovered (idempotent)
# Uses AGENT_DIRECTORIES env var or defaults to framework agents only
discover_agents()

app.include_router(rest_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7001))
    # Respect LOG_LEVEL env var; fallback to INFO
    uvicorn_log_level = os.environ.get("LOG_LEVEL", "INFO").lower()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=uvicorn_log_level)
