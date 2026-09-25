@echo off
title TI SLEP VALLE DIGUILLIN - CONTROL DE VISITAS Y SOPORTE TI
echo =====================================================================
echo    TI SLEP VALLE DIGUILLIN - SISTEMA DE VISITAS Y SOPORTE TI
echo =====================================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%CD%

echo [1/2] Verificando dependencias de Python...
python -m pip install fastapi uvicorn pydantic openpyxl psycopg2-binary >nul 2>&1

echo [2/2] Iniciando aplicacion web y conexion de base de datos...
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
