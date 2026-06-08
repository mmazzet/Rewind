from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, tapes

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1")
app.include_router(tapes.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    }

    if (
        request.method in state_changing_methods
        and request.url.path not in exempt_paths
    ):
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
