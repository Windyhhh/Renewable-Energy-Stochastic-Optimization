@echo off
echo ========================================
echo 使用Conda测试项目
echo ========================================
echo.

REM 初始化conda
call conda activate base

echo 检查Python版本...
python --version
echo.

echo 安装依赖包...
pip install -r requirements.txt
echo.

echo 运行测试脚本...
python test_installation.py
echo.

echo ========================================
echo 测试完成
echo ========================================
pause

