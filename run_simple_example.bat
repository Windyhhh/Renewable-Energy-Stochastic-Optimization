@echo off
echo ========================================
echo 运行简化示例
echo ========================================
echo.

REM 尝试不同的Python命令
where python >nul 2>&1
if %errorlevel% == 0 (
    python examples\simple_example.py
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% == 0 (
    python3 examples\simple_example.py
    goto :end
)

where py >nul 2>&1
if %errorlevel% == 0 (
    py examples\simple_example.py
    goto :end
)

echo 错误: 未找到Python！
echo 请先安装Python，参考INSTALL.md
pause
exit /b 1

:end
echo.
echo ========================================
echo 运行完成
echo ========================================
pause

