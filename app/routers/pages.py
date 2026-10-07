from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent
    / "templates"
)


def load_html(filename: str) -> str:
    return (TEMPLATE_DIR / filename).read_text(encoding="utf-8")

@router.get("/",response_class=HTMLResponse)
def home():
    return load_html("home.html")

@router.get("/payment/success",response_class=HTMLResponse)
def payment_success():
    return load_html("success.html")

@router.get("/payment/failed",response_class=HTMLResponse)
def payment_failed():
    return load_html("failed.html")