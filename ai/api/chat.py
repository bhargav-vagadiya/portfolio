import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402 — FastAPI ASGI app
from starlette.middleware.base import BaseHTTPMiddleware


class StripApiPrefix(BaseHTTPMiddleware):
    """Vercel sends /api/chat but FastAPI routes are /chat — strip /api prefix."""
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/"):
            request.scope["path"] = request.url.path[4:]  # /api/chat → /chat
        return await call_next(request)


app.add_middleware(StripApiPrefix)
