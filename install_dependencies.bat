@echo off
echo ========================================
echo 安装项目依赖
echo ========================================
echo.

REM 尝试不同的Python命令
where python >nul 2>&1
if %errorlevel% == 0 (
    echo 使用 python 命令...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% == 0 (
    echo 使用 python3 命令...
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    goto :end
)

where py >nul 2>&1
if %errorlevel% == 0 (
    echo 使用 py 命令...
    py -m pip install --upgrade pip
    py -m pip install -r requirements.txt
    goto :end
)

echo 错误: 未找到Python！
echo 请先安装Python，参考INSTALL.md
pause
exit /b 1

:end
echo.
echo ========================================
echo 依赖安装完成
echo 现在可以运行: run_simple_example.bat
echo ========================================
pause

