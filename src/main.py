from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routers import auth_router, user_router

from .config import settings


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


app.include_router(auth_router, tags=["AUTH"])
app.include_router(user_router, tags=["USER"])


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url=str(request.url) + "docs")