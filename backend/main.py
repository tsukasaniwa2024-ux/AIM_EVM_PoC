from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="EVM 輸入帳票自動化システム")

# フロントエンド配信
app.mount("/static", StaticFiles(directory="/app/../frontend"), name="static")

@app.get("/")
def root():
    return FileResponse("/app/../frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}
