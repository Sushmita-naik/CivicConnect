from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.database import engine, Base
from backend.routes import complaints, ml, auth, dashboard, profile, notifications


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Community Problem Reporting Platform",
    description="A platform for reporting and managing community problems",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include complaint APIs
app.include_router(complaints.router)
app.include_router(complaints.router, prefix="/api")
app.include_router(ml.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(notifications.router)

# Home page
@app.get("/")
def home():
    return {
        "message": "Welcome to Community Problem Reporting Platform!",
        "status": "success"
    }


# Health check
@app.get("/health")
def health_check():
    return {
        "message": "Backend is running successfully",
        "status": "healthy"
    }
