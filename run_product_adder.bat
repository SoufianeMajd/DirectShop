@echo off
echo ========================================
echo    Automatic Product Adder
echo ========================================
echo.

echo Installing required packages...
pip install -r requirements_products.txt

echo.
echo Choose which script to run:
echo 1. Simple Product Adder (recommended, max 20 products)
echo 2. Advanced Product Adder (up to 100 products from multiple APIs)
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Running Simple Product Adder...
    python simple_product_adder.py
) else if "%choice%"=="2" (
    echo.
    echo Running Advanced Product Adder...
    python auto_add_products.py
) else (
    echo Invalid choice. Running Simple Product Adder by default...
    python simple_product_adder.py
)

echo.
echo Press any key to exit...
pause >nul