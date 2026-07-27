@echo off

REM Quality check script for Windows development
REM Run all checks before committing

setlocal enabledelayedexpansion

echo 🔍 Korame Quality Check
echo =======================
echo.

echo 📝 Formatting with Black...
python -m black app\ tests\
if errorlevel 1 (
    echo ❌ Black failed
    exit /b 1
)
echo ✓ Black done
echo.

echo 🚨 Linting with Flake8...
python -m flake8 app\ tests\
if errorlevel 1 (
    echo ⚠️  Some linting issues found
) else (
    echo ✓ Flake8 done
)
echo.

echo 🔐 Type checking with MyPy...
python -m mypy app\
if errorlevel 1 (
    echo ⚠️  Some type issues found
) else (
    echo ✓ MyPy done
)
echo.

echo 🧪 Running tests...
python -m pytest tests\ -v --cov=app --cov-report=term-missing
if errorlevel 1 (
    echo ❌ Tests failed
    exit /b 1
)
echo ✓ Tests done
echo.

echo ✅ Quality check complete!

