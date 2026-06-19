import random
import string
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import URL

router = APIRouter()


class ShortenRequest(BaseModel):
    url: str


def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@router.post("/shorten")
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    code = generate_code()
    while db.query(URL).filter(URL.code == code).first():
        code = generate_code()

    entry = URL(code=code, original=payload.url)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"code": entry.code, "short_url": f"/r/{entry.code}"}


@router.get("/urls")
def list_urls(db: Session = Depends(get_db)):
    return db.query(URL).order_by(URL.id.desc()).all()


@router.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.code == code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="URL not found")
    entry.clicks += 1
    db.commit()
    return RedirectResponse(url=entry.original, status_code=302)
