from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.models import router as models_router

app = FastAPI(
    title="AutoArchive API",
    version="0.1.0",
)

# CORS (needed later for Astro/Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",   # Astro dev
        "http://127.0.0.1:4321",
        "http://localhost:3000",   # just in case
        "https://autoarchive-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check (very important for sanity + deployment)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Register API routes
app.include_router(models_router)