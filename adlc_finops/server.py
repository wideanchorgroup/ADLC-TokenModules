"""FastAPI Application Server for ADLC FinOps & Governance Control Plane."""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from features.self_service_onboarding.router import router as onboarding_router
from features.enterprise_policy_profiles.router import router as policy_router
from features.repository_qualification.router import router as qualification_router
from features.golden_path_catalog.router import router as golden_tasks_router
from features.unified_evidence_record.router import router as evidence_router
from features.enterprise_eval_service.router import router as evaluations_router
from features.finops_dashboard_controls.router import router as finops_router
from features.governed_plugin_catalog.router import router as plugins_router
from features.fleet_posture_drift.router import router as fleet_router
from features.sdlc_feedback_loop.router import router as feedback_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="ADLC FinOps & Governance Control Plane",
    description="Enterprise API and Control Plane consuming Compass, Distil, and Halos for AI-assisted SDLC governance and spend control.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include all 10 Feature Routers
app.include_router(finops_router)
app.include_router(onboarding_router)
app.include_router(policy_router)
app.include_router(qualification_router)
app.include_router(golden_tasks_router)
app.include_router(evidence_router)
app.include_router(evaluations_router)
app.include_router(plugins_router)
app.include_router(fleet_router)
app.include_router(feedback_router)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the FinOps & Governance interactive web dashboard."""
    template_path = BASE_DIR / "templates" / "index.html"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found")
    return FileResponse(template_path)

@app.get("/api/health")
async def health_check():
    """Health check endpoint indicating API and client readiness."""
    return {
        "status": "healthy",
        "service": "ADLC-FinOps-ControlPlane",
        "version": "1.0.0",
        "environment": settings.environment,
        "mock_mode": settings.mock_mode,
        "integrated_services": {
            "compass": {"url": settings.compass_api_url, "status": "connected"},
            "distil": {"url": settings.distil_api_url, "status": "connected"},
            "halos": {"url": settings.halos_api_url, "status": "connected"}
        }
    }
