from fastapi import FastAPI
from app.database import Base, engine
from app.routers import urls

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

app.include_router(urls.router)


@app.get("/health")
def health():
    return {"status": "ok"}
