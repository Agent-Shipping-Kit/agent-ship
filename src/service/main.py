'''
This is the main file for the backend.
'''
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
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
    docs_url="/swagger",  # Swagger UI at /swagger (API reference)
    redoc_url="/redoc",   # ReDoc at /redoc (alternative API docs)
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

# Serve MkDocs documentation at /docs (single source of truth)
# If not built locally, show a helpful page with links
docs_site_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "site")
if os.path.exists(docs_site_path) and os.path.exists(os.path.join(docs_site_path, "index.html")):
    # Mount static files for MkDocs site at /docs
    app.mount("/docs", StaticFiles(directory=docs_site_path, html=True), name="docs")
else:
    # If docs not built, show a helpful page with links
    @app.get("/docs", response_class=HTMLResponse)
    @app.get("/docs/{path:path}", response_class=HTMLResponse)
    async def docs_info(path: str = ""):
        """Show documentation links page."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AgentShip Documentation</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                       max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .link { display: block; margin: 15px 0; padding: 15px; 
                        background: #f5f5f5; border-radius: 5px; text-decoration: none; 
                        color: #0066cc; }
                .link:hover { background: #e0e0e0; }
                .api-link { background: #e3f2fd; }
            </style>
        </head>
        <body>
            <h1>📚 AgentShip Documentation</h1>
            <p>Choose your documentation source:</p>
            <a href="/swagger" class="link api-link">
                <strong>API Documentation (Swagger)</strong><br>
                <small>Interactive API reference and testing</small>
            </a>
            <a href="https://harshuljain13.github.io/ship-ai-agents/" class="link" target="_blank">
                <strong>Framework Documentation (GitHub Pages)</strong><br>
                <small>Complete guides, tutorials, and examples</small>
            </a>
            <a href="/redoc" class="link">
                <strong>ReDoc API Documentation</strong><br>
                <small>Alternative API documentation format</small>
            </a>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

# Ensure agents are discovered (idempotent)
# Uses AGENT_DIRECTORIES env var or defaults to framework agents only
discover_agents()

app.include_router(rest_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7001))
    # Respect LOG_LEVEL env var; fallback to INFO
    uvicorn_log_level = os.environ.get("LOG_LEVEL", "INFO").lower()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=uvicorn_log_level)
