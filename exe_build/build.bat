@echo off
echo ================================
echo  AIM EVM exe ビルドスクリプト
echo ================================
echo.

:: Pythonの確認
python --version > nul 2>&1
if errorlevel 1 (
    echo [エラー] Pythonがインストールされていません。
    echo https://www.python.org/downloads/ からインストールしてください。
    pause
    exit /b 1
)

:: pipの確認・PyInstallerインストール
echo PyInstallerをインストールしています...
pip install pyinstaller > nul 2>&1

:: backendの依存関係インストール
echo 依存ライブラリをインストールしています...
pip install -r ..\backend\requirements.txt > nul 2>&1

:: exe化実行
echo.
echo exe化を開始します（数分かかります）...
pyinstaller ^
    --name "AIM_EVM" ^
    --onefile ^
    --console ^
    --add-data "..\backend;backend" ^
    --add-data "..\frontend;frontend" ^
    --hidden-import uvicorn ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols ^
    --hidden-import uvicorn.protocols.http ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.lifespan ^
    --hidden-import uvicorn.lifespan.on ^
    --hidden-import fastapi ^
    --hidden-import sqlalchemy ^
    --hidden-import openai ^
    --hidden-import pdf2image ^
    --hidden-import openpyxl ^
    --hidden-import pandas ^
    launcher.py

echo.
if exist dist\AIM_EVM.exe (
    echo ================================
    echo  ビルド成功！
    echo  dist\AIM_EVM.exe が作成されました
    echo ================================
    echo.
    echo 配布するファイル：
    echo   - dist\AIM_EVM.exe
    echo   - .env.example を .env にリネームして同じフォルダに配置
) else (
    echo [エラー] ビルドに失敗しました。
)

pause
