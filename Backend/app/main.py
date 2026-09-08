from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.query import router as query_router


app = FastAPI(
    title="IP-SAKTI Sahayak API",
    description=(
        "Multilingual AI assistant for Ayurvedic intellectual property "
        "and legal-regulatory guidance."
    ),
    version="0.1.0"
)


# Allow the Next.js frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this before production deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {
        "message": "IP-SAKTI backend is running!",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


app.include_router(query_router)