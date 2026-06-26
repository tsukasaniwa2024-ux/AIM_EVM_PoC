@echo off
chcp 65001 > nul
echo ================================
echo  AIM EVM exe Build Script
echo ================================
echo.

python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing PyInstaller...
pip install pyinstaller > nul 2>&1

echo Installing dependencies...
pip install -r ..\backend\requirements.txt > nul 2>&1

echo.
echo Building exe... (this may take a few minutes)
pyinstaller ^
    --name "EVM_Import_Tool" ^
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
if exist dist\EVM_Import_Tool.exe (
    echo ================================
    echo  Build successful!
    echo  dist\EVM_Import_Tool.exe created
    echo ================================
    echo.
    echo Files to distribute:
    echo   - dist\EVM_Import_Tool.exe
    echo   - .env (rename from .env.example and set API key)
) else (
    echo [ERROR] Build failed.
)

pause
