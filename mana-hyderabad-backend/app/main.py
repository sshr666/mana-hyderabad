from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import admin, complaints, uploads
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Mana Hyderabad Backend",
    description="Backend foundation for the Mana Hyderabad civic complaint platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
def sqlalchemy_exception_handler(_request, _exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Database failure"})


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(uploads.router)
