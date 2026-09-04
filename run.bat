@echo off
title TI SLEP VALLE DIGUILLIN - SUBDIRECCION DE PLANIFICACION Y CONTROL DE GESTION
echo =====================================================================
echo    TI SLEP VALLE DIGUILLIN
echo    SUBDIRECCION DE PLANIFICACION Y CONTROL DE GESTION
echo =====================================================================
echo.

cd /d "%~dp0"

echo [1/2] Verificando dependencias de Python...
python -m pip install fastapi uvicorn pydantic openpyxl >nul 2>&1

echo [2/2] Iniciando aplicacion web y base de datos...
echo.
echo =====================================================================
echo Accede en tu navegador a:
echo    http://localhost:8080   (o http://localhost:8000)
echo.
echo Credenciales de acceso:
echo    Usuario:     admin@soporteti.cl
echo    Contrasena:  admin123
echo =====================================================================
echo.
python backend/server.py
pause

