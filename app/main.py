from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import Base, get_engine
    Base.metadata.create_all(bind=get_engine())
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(urls.router)
