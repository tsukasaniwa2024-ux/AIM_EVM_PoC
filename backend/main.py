from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 作成したAPIルーター
from routers import upload


# FastAPIアプリ作成
app = FastAPI(
    title="EVM 輸入帳票自動化システム",
    version="1.0"
)


# =========================
# フロントエンド配信
# =========================

# frontend配下の
# index.html
# css
# js
# を配信する
app.mount(
    "/static",
    StaticFiles(directory="/frontend"),
    name="static"
)


# トップページ
# ブラウザアクセス時に
# frontend/index.htmlを返す
@app.get("/")
def root():

    return FileResponse(
        "/frontend/index.html"
    )


# ヘルスチェック
# Docker起動確認などで利用
@app.get("/health")
def health():

    return {
        "status": "ok"
    }



# =========================
# APIルーター登録
# =========================

# upload.py のAPIを登録
#
# upload.py
# @router.post("/process")
#
# 実際:
# POST /api/process
app.include_router(
    upload.router,
    prefix="/api"
)