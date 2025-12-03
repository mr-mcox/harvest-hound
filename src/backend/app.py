"""
Harvest Hound - FastAPI Application
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes import router

app = FastAPI(title="Harvest Hound")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes first (so /api/* takes precedence)
app.include_router(router)

# Static directory for built frontend
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def serve_frontend():
    """Serve the built frontend index.html"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}


# Mount static files for assets (JS, CSS, etc.)
# Must come after explicit routes
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
