from fastapi import APIRouter
from app.api.v1 import (
    auth, items, categories, requests, reviews, messages,
    ai, statistics, health, favorites, uploads, admin, benchmark,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(items.router)
api_router.include_router(categories.router)
api_router.include_router(requests.router)
api_router.include_router(reviews.router)
api_router.include_router(messages.router)
api_router.include_router(ai.router)
api_router.include_router(statistics.router)
api_router.include_router(health.router)
api_router.include_router(favorites.router)
api_router.include_router(uploads.router)
api_router.include_router(admin.router)
api_router.include_router(benchmark.router)
