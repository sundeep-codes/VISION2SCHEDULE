from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registrations
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(scan_router.router)
app.include_router(nearby_router.router)
app.include_router(calendar.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Vision2Schedule API is running.", "status": "healthy"}
