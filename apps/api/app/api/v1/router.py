from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    analytics,
    audit_logs,
    auth,
    complaints,
    health,
    institutions,
    notifications,
    overlaps,
    reference,
    work_queue,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(institutions.router)
api_router.include_router(complaints.router)
api_router.include_router(overlaps.router)
api_router.include_router(reference.router)
api_router.include_router(notifications.router)
api_router.include_router(work_queue.router)
api_router.include_router(analytics.router)
api_router.include_router(audit_logs.router)
api_router.include_router(admin.router)
