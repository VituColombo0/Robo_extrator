@echo off
echo ==========================================
echo   Recompilando Robo_Extrator...
echo ==========================================
echo.

REM Garante que PyInstaller esta instalado
python -m pip install pyinstaller --quiet

echo [1/2] Compilando com PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Robo_Extrator" ^
    "scripts\robo_extrator_final.py"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] A compilacao falhou! Verifique o log acima.
    pause
    exit /b 1
)

echo.
echo [2/2] Limpando arquivos temporarios de build...
rmdir /s /q build
del /q Robo_Extrator.spec

echo.
echo ==========================================
echo   PRONTO! Executable atualizado em:
echo   dist\Robo_Extrator\Robo_Extrator.exe
echo ==========================================
echo.
pause
