from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import router
from app.model import model_loader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: attempt loading approved artifact once
    model_loader.load_artifact()
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="Real Estate Price Prediction — Inference Service",
    version="1.0.0-scaffold",
    description="Standalone inference HTTP service for evaluating Indian residential property prices.",
    lifespan=lifespan,
)

app.include_router(router)
