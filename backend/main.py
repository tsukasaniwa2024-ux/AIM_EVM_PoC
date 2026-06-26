import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import upload

app = FastAPI(title="EVM 輸入帳票自動化システム")

# フロントエンドのパス（Docker環境とexe環境で切り替え）
FRONTEND_DIR = os.environ.get("FRONTEND_DIR", "/frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(upload.router, prefix="/api")
