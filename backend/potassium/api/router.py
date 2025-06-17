from fastapi import APIRouter

from potassium.api import scheduler as scheduler_router
from potassium.api import signals as signals_router

api_router = APIRouter()

router_v1 = APIRouter()
router_v1.include_router(scheduler_router.router, prefix="/scheduler", tags=["Scheduler"])
router_v1.include_router(signals_router.router, prefix="/signal", tags=["Signals"])

api_router.include_router(router_v1, prefix="/v1", tags=["v1"])
