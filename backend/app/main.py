from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.middleware.error_handlers import register_error_handlers
from app.routers import auth, spotify, tapes, tracks

app = FastAPI()

register_error_handlers(app)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tapes.router, prefix="/api/v1")
app.include_router(spotify.router, prefix="/api/v1")
app.include_router(tracks.router, prefix="/api/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    state_changing_methods = {"POST", "PATCH", "DELETE", "PUT"}
    exempt_paths = {
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/verify-email",
    }

    if (
        request.method in state_changing_methods
        and request.url.path not in exempt_paths
    ):
        # Only check CSRF if the user is authenticated (has access_token cookie)
        access_token = request.cookies.get("access_token")
        if access_token:
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_cookie or csrf_cookie != csrf_header:
                return JSONResponse(
                    status_code=403, content={"error": "CSRF validation failed"}
                )

    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}
