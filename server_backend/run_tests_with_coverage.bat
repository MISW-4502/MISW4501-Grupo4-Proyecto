@echo off
echo === Ejecutando pruebas con coverage ===

:: AUTH
echo.
echo == Auth ==
cd auth
set PYTHONPATH=src
pytest --cov=src --cov-report=html --cov-report=term test
cd ..

:: TRUCK
echo.
echo == Truck ==
cd truck
set PYTHONPATH=src
pytest --cov=src --cov-report=html:htmlcov_truck --cov-report=term test
cd ..

:: MANUFACTURER
echo.
echo == Manufacturer ==
cd manufacturer
set PYTHONPATH=src
pytest --cov=src --cov-report=html:htmlcov_manufacturer --cov-report=term test
cd ..

:: INVENTARY
echo.
echo == Inventary ==
cd inventary
set PYTHONPATH=src
pytest --cov=src --cov-report=html:htmlcov_inventary --cov-report=term test
cd ..

echo.
echo ✅ Todas las pruebas fueron ejecutadas con reporte de cobertura.

:: SALES
echo.
echo == Sales ==
cd sales
set PYTHONPATH=src
pytest --cov=src --cov-report=html:htmlcov_inventary --cov-report=term test
cd ..

echo.
echo ✅ Todas las pruebas fueron ejecutadas con reporte de cobertura.