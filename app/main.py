from fastapi import FastAPI
from app.routers import urls

app = FastAPI(title="URL Shortener")

app.include_router(urls.router)


@app.on_event("startup")
def startup():
    from app.database import Base, get_engine
    Base.metadata.create_all(bind=get_engine())


@app.get("/health")
def health():
    return {"status": "ok"}
