import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, SessionLocal, engine
from . import models  # noqa: F401 确保模型已注册
from .mock_data import seed_mock_data
from .routers import matches


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.use_mock_data:
        db = SessionLocal()
        try:
            seed_mock_data(db)
        finally:
            db.close()
    yield


app = FastAPI(title="足球比分预测", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "mock_data": settings.use_mock_data}


# 阶段 5 将 index.html 放入 frontend/，由此处静态托管在根路径
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=False)
