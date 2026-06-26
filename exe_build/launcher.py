"""
AIM EVM 輸入帳票自動化システム 起動スクリプト
"""
import os
import sys
import time
import threading
import webbrowser

# exeとして実行されている場合のパス解決
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ENV_FILE = os.path.join(APP_DIR, ".env")

# 環境変数の読み込み
def load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# frontendのパスを環境変数で渡す（main.pyで参照）
os.environ["FRONTEND_DIR"] = FRONTEND_DIR

# backendをパスに追加
sys.path.insert(0, BACKEND_DIR)

PORT = 8001
URL = f"http://localhost:{PORT}"


def open_browser():
    time.sleep(2)
    webbrowser.open(URL)


def main():
    print("=" * 50)
    print("  AIM EVM 輸入帳票自動化システム")
    print("=" * 50)
    print(f"\nサーバーを起動しています...")
    print(f"ブラウザで {URL} を開きます\n")
    print("終了するには このウィンドウを閉じてください\n")

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        app_dir=BACKEND_DIR,
    )


if __name__ == "__main__":
    main()
