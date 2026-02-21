import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import engine, Base

import auth
import events
import scan_router
import nearby_router
import calendar

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vision2Schedule API",
    description="Backend for Vision2Schedule — OCR Flyer to Calendar automation.",
    version="1.0.0"
)

# CORS Middleware
origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update to allow all for simplicity, or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registrations under /api
app.include_router(auth.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(scan_router.router, prefix="/api")
app.include_router(nearby_router.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")

@app.get("/api/", tags=["Health"])
def root():
    return {"message": "Vision2Schedule API is running.", "status": "healthy"}

# Mount the React dist folder using StaticFiles
dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(dist_dir):
    # Mount assets directory directly
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Add fallback route to serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Prevent accessing files outside of dist_dir
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side routing
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return {"error": "Frontend dist folder not found. Please run npm run build in frontend."}
