from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import pages, payment


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount(
    "/templates",
    StaticFiles(
        directory=str(BASE_DIR / "templates")
    ),
    name="templates"
)


app.include_router(pages.router)
app.include_router(payment.router)