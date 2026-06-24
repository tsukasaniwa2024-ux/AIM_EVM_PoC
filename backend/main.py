from fastapi import FastAPI

# 作成したルーターを読み込む
# upload.py にAPI処理を分離する
from routers import upload


# FastAPIアプリケーション作成
app = FastAPI(
    title="EVM 輸入帳票自動化システム",
    version="1.0"
)


# upload.py のルーターを登録
# prefix="/api" を付けることで
# upload.py側のURLは /api から始まる
#
# 例:
# upload.py
# @router.post("/process")
#
# 実際のAPI
# POST /api/process
app.include_router(
    upload.router,
    prefix="/api"
)


# 動作確認用エンドポイント
# サーバー起動確認で使用
@app.get("/")
def root():

    return {
        "message": "EVM Import System API"
    }