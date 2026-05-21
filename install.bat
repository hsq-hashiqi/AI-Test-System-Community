@echo off
chcp 65001 >nul
title AI???? - ????

echo ========================================
echo    ?? AI???? - ??????
echo ========================================
echo.

:: ?? Python
echo [1/4] ?? Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ? Python ???
    echo    ???? Python 3.10+
    pause
    exit /b 1
)
echo ? Python: 
python --version
echo.

:: ?? pip
echo [2/4] ?? pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ? pip ???
    pause
    exit /b 1
)
echo ? pip: 
pip --version
echo.

:: ????
echo [3/4] ?? Python ??...
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if errorlevel 1 (
    echo ? ??????
    pause
    exit /b 1
)
echo ? ??????
echo.

:: ????
echo [4/4] ??????...
python generate_key.py
echo.

echo ========================================
echo    ? ?????
echo ========================================
echo.
echo ????: python start_system.py
echo API??: http://localhost:8000/docs
echo.
pause
