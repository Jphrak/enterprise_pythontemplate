# Development scripts for the project (Windows)
# Usage: .\scripts.ps1 <command>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    [string]$File = ""
)

$venv = ".\.venv\Scripts\python.exe"

function Test-Venv {
    if (-not (Test-Path $venv)) {
        Write-Host "Error: Virtual environment not found at $venv" -ForegroundColor Red
        Write-Host "Create one with: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
}

switch ($Command.ToLower()) {
    "run" {
        Test-Venv
        Write-Host "Running application..." -ForegroundColor Green
        & $venv app.py
    }
    "install" {
        Test-Venv
        Write-Host "Installing production dependencies..." -ForegroundColor Green
        & $venv -m pip install -r requirements.txt
    }
    "install-dev" {
        Test-Venv
        Write-Host "Installing development dependencies..." -ForegroundColor Green
        & $venv -m pip install -r requirements-dev.txt
    }
    "format" {
        Test-Venv
        Write-Host "Formatting code with ruff..." -ForegroundColor Green
        & $venv -m ruff format .
    }
    "check" {
        Test-Venv
        Write-Host "Checking code with ruff..." -ForegroundColor Green
        & $venv -m ruff check .
    }
    "fix" {
        Test-Venv
        Write-Host "Fixing code issues with ruff..." -ForegroundColor Green
        & $venv -m ruff check . --fix
    }
    "check-file" {
        Test-Venv
        if ($File -eq "") {
            Write-Host "Please specify a file with -File parameter" -ForegroundColor Red
            exit 1
        }
        Write-Host "Checking file: $File" -ForegroundColor Green
        & $venv -m ruff check $File
    }
    "fix-file" {
        Test-Venv
        if ($File -eq "") {
            Write-Host "Please specify a file with -File parameter" -ForegroundColor Red
            exit 1
        }
        Write-Host "Fixing file: $File" -ForegroundColor Green
        & $venv -m ruff check $File --fix
    }
    "mypy" {
        Test-Venv
        Write-Host "Type checking with mypy..." -ForegroundColor Green
        & $venv -m mypy
    }
    "lint-all" {
        Test-Venv
        Write-Host "Running all linting checks..." -ForegroundColor Green
        Write-Host "1. Ruff check..." -ForegroundColor Yellow
        & $venv -m ruff check .
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "2. Mypy type checking..." -ForegroundColor Yellow
        & $venv -m mypy
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "All linting checks completed successfully!" -ForegroundColor Green
    }
    "test" {
        Test-Venv
        Write-Host "Running tests..." -ForegroundColor Green
        & $venv -m pytest tests/
    }
    "test-cov" {
        Test-Venv
        Write-Host "Running tests with coverage..." -ForegroundColor Green
        & $venv -m coverage run -m pytest tests/
        & $venv -m coverage report --show-missing
    }
    "clean" {
        Write-Host "Cleaning cache and build artifacts..." -ForegroundColor Green
        Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Recurse -Directory -Name ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Recurse -Directory -Name ".mypy_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Recurse -Directory -Name ".ruff_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Recurse -File -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "build", "dist", "*.egg-info", ".coverage", "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleanup completed!" -ForegroundColor Green
    }
    "build" {
        Test-Venv
        Write-Host "Running full build pipeline..." -ForegroundColor Green
        $errors = @()

        Write-Host "1. Checking formatting with ruff..." -ForegroundColor Yellow
        & $venv -m ruff format --check .
        if ($LASTEXITCODE -ne 0) { $errors += "Formatting check failed" }

        Write-Host "2. Linting with ruff..." -ForegroundColor Yellow
        & $venv -m ruff check .
        if ($LASTEXITCODE -ne 0) { $errors += "Linting failed" }

        Write-Host "3. Type checking with mypy..." -ForegroundColor Yellow
        & $venv -m mypy
        if ($LASTEXITCODE -ne 0) { $errors += "Type checking failed" }

        Write-Host "4. Testing with pytest..." -ForegroundColor Yellow
        & $venv -m pytest tests/
        if ($LASTEXITCODE -ne 0) { $errors += "Tests failed" }

        if ($errors.Count -gt 0) {
            Write-Host "`nBuild failed with the following errors:" -ForegroundColor Red
            foreach ($err in $errors) {
                Write-Host "  - $err" -ForegroundColor Red
            }
            exit 1
        }
        Write-Host "Build completed successfully!" -ForegroundColor Green
    }

    "dev-setup" {
        Write-Host "Setting up development environment..." -ForegroundColor Green
        if (-not (Test-Path ".venv")) {
            Write-Host "Creating virtual environment..." -ForegroundColor Yellow
            python -m venv .venv
        }
        Write-Host "Python version: $(& $venv --version)" -ForegroundColor Yellow
        & $venv -m pip install -r requirements-dev.txt
        Write-Host "Development environment setup complete!" -ForegroundColor Green
    }
    "dev-check" {
        Test-Venv
        Write-Host "Running quick development check..." -ForegroundColor Green
        $errors = @()

        & $venv -m ruff format .
        if ($LASTEXITCODE -ne 0) { $errors += "Formatting failed" }

        & $venv -m ruff check . --fix
        if ($LASTEXITCODE -ne 0) { $errors += "Linting failed" }

        & $venv -m coverage run -m pytest tests/
        if ($LASTEXITCODE -ne 0) { $errors += "Tests failed" }

        & $venv -m coverage report

        if ($errors.Count -gt 0) {
            Write-Host "`nDevelopment check failed with the following errors:" -ForegroundColor Red
            foreach ($err in $errors) {
                Write-Host "  - $err" -ForegroundColor Red
            }
            exit 1
        }
        Write-Host "Quick development check completed!" -ForegroundColor Green
    }
    "help" {
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  run          - Run the application"
        Write-Host "  install      - Install production dependencies"
        Write-Host "  install-dev  - Install development dependencies"
        Write-Host "  format       - Format code with ruff"
        Write-Host "  check        - Check code with ruff"
        Write-Host "  fix          - Fix code issues with ruff"
        Write-Host "  check-file   - Check specific file (use -File parameter)"
        Write-Host "  fix-file     - Fix specific file (use -File parameter)"
        Write-Host "  mypy         - Type check main code"
        Write-Host "  lint-all     - Run all linting checks"
        Write-Host "  test         - Run tests"
        Write-Host "  test-cov     - Run tests with coverage"
        Write-Host "  clean        - Clean cache and build artifacts"
        Write-Host "  build        - Run format, lint, type, and test checks"
        Write-Host "  dev-setup    - Set up development environment"
        Write-Host "  dev-check    - Quick development check (format + check + test)"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\scripts.ps1 format"
        Write-Host "  .\scripts.ps1 check-file -File 'src\utils\logger.py'"
        Write-Host "  .\scripts.ps1 build"
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\scripts.ps1 help' to see available commands" -ForegroundColor Yellow
        exit 1
    }
}
