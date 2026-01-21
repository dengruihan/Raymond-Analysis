from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from backend.models import init_db
from backend.api import track_router, stats_router, websocket_router
from backend.api.sankey import router as sankey_router
from backend.utils.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(track_router)
app.include_router(stats_router)
app.include_router(websocket_router)
app.include_router(sankey_router)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/tracker.js")
async def tracker():
    with open("tracking/raymond-tracker.js", "r", encoding="utf-8") as f:
        return Response(
            content=f.read(),
            media_type="application/javascript; charset=utf-8"
        )

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    with open("frontend/templates/test.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/tracker-test", response_class=HTMLResponse)
async def tracker_test_page():
    with open("frontend/templates/tracker-test.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
