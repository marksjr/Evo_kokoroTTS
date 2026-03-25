@echo off
chcp 65001 >nul 2>&1
title Evo KokoroTTS - Servidor
cd /d "%~dp0"

echo.
echo  Evo KokoroTTS - Iniciando servidor...
echo  Interface web: http://localhost:8880
echo  Pressione Ctrl+C para encerrar.
echo.

:: Adicionar ferramentas locais ao PATH se existirem
if exist "%~dp0ffmpeg\ffmpeg.exe" set "PATH=%~dp0ffmpeg;%PATH%"
if exist "%~dp0ffmpeg\bin\ffmpeg.exe" set "PATH=%~dp0ffmpeg\bin;%PATH%"
if exist "%~dp0espeak-ng\espeak-ng.exe" set "PATH=%~dp0espeak-ng;%PATH%"
if exist "%~dp0espeak-ng\command_line\espeak-ng.exe" set "PATH=%~dp0espeak-ng\command_line;%PATH%"
if exist "C:\Program Files\eSpeak NG\espeak-ng.exe" set "PATH=C:\Program Files\eSpeak NG;%PATH%"

:: Detectar qual Python usar
if exist "%~dp0python_embedded\python.exe" (
    "%~dp0python_embedded\python.exe" start.py
) else if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" start.py
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  Nenhum Python configurado foi encontrado.
        echo  Execute install.bat antes de iniciar o servidor.
        echo.
        pause
        exit /b 1
    )
    python start.py
)

pause
