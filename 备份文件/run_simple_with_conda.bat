@echo off
echo ========================================
echo 使用Conda运行简化示例
echo ========================================
echo.

REM 初始化conda
call conda activate base

echo 运行简化示例...
python examples\simple_example.py

echo.
echo ========================================
echo 运行完成
echo ========================================
pause

