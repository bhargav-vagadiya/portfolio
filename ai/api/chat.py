import sys
import os

# main.py is in the same directory as this file (api/ is inside ai/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402 — FastAPI ASGI app
