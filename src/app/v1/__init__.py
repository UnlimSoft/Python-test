from .routers.cities import router as cities
from .routers.picnics import router as picnics
from .routers.users import router as users

from fastapi import APIRouter

router = APIRouter(prefix='/v1')
router.include_router(cities)
router.include_router(picnics)
router.include_router(users)
