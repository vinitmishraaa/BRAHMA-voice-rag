from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import close_pipeline, router
from config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


# =============================================================
# CORS
# =============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================
# ROUTES
# =============================================================

app.include_router(router)


# =============================================================
# SHUTDOWN
# =============================================================

@app.on_event("shutdown")
def shutdown_event() -> None:
    close_pipeline()