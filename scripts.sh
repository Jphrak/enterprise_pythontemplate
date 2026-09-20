#!/bin/bash
# Development scripts for the project (Linux/Mac)
# Usage: ./scripts.sh <command> [--file <filename>]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Virtual environment python executable
VENV_PYTHON="./.venv/bin/python"

# Parse command line arguments
COMMAND=""
FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            FILE="$2"
            shift 2
            ;;
        *)
            if [[ -z "$COMMAND" ]]; then
                COMMAND="$1"
            else
                echo -e "${RED}Error: Unknown argument $1${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$COMMAND" ]]; then
    echo -e "${RED}Error: No command specified${NC}"
    echo -e "${YELLOW}Use './scripts.sh help' to see available commands${NC}"
    exit 1
fi

COMMAND_LOWER="$(printf '%s' "$COMMAND" | tr '[:upper:]' '[:lower:]')"

# Function to check if virtual environment exists
check_venv() {
    if [[ ! -f "$VENV_PYTHON" ]]; then
        echo -e "${RED}Error: Virtual environment not found at $VENV_PYTHON${NC}"
        echo -e "${YELLOW}Please create a virtual environment first: python -m venv .venv${NC}"
        exit 1
    fi
}

case "$COMMAND_LOWER" in
    "run")
        echo -e "${GREEN}Running application...${NC}"
        check_venv
        "$VENV_PYTHON" app.py
        ;;
    "install")
        echo -e "${GREEN}Installing production dependencies...${NC}"
        check_venv
        "$VENV_PYTHON" -m pip install -r requirements.txt
        ;;
    "install-dev")
        echo -e "${GREEN}Installing development dependencies...${NC}"
        check_venv
        "$VENV_PYTHON" -m pip install -r requirements-dev.txt
        ;;
    "format")
        echo -e "${GREEN}Formatting code with ruff...${NC}"
        check_venv
        "$VENV_PYTHON" -m ruff format .
        ;;
    "check")
        echo -e "${GREEN}Checking code with ruff...${NC}"
        check_venv
        "$VENV_PYTHON" -m ruff check .
        ;;
    "fix")
        echo -e "${GREEN}Fixing code issues with ruff...${NC}"
        check_venv
        "$VENV_PYTHON" -m ruff check . --fix
        ;;
    "check-file")
        if [[ -z "$FILE" ]]; then
            echo -e "${RED}Please specify a file with --file parameter${NC}"
            exit 1
        fi
        echo -e "${GREEN}Checking file: $FILE${NC}"
        check_venv
        "$VENV_PYTHON" -m ruff check "$FILE"
        ;;
    "fix-file")
        if [[ -z "$FILE" ]]; then
            echo -e "${RED}Please specify a file with --file parameter${NC}"
            exit 1
        fi
        echo -e "${GREEN}Fixing file: $FILE${NC}"
        check_venv
        "$VENV_PYTHON" -m ruff check "$FILE" --fix
        ;;
    "mypy")
        echo "Type checking with mypy..."
        check_venv
        "$VENV_PYTHON" -m mypy
        ;;
    "lint-all")
        echo "Running all linting checks..."
        check_venv
        errors=()

        echo "1. Ruff check..."
        "$VENV_PYTHON" -m ruff check . || errors+=("Ruff check failed")

        echo "2. Mypy type checking..."
        "$VENV_PYTHON" -m mypy || errors+=("Type checking failed")

        if [ ${#errors[@]} -gt 0 ]; then
            echo ""
            echo "Linting failed with the following errors:"
            for err in "${errors[@]}"; do
                echo "  - $err"
            done
            exit 1
        fi
        echo "All linting checks completed successfully!"
        ;;
    "test")
        echo -e "${GREEN}Running tests...${NC}"
        check_venv
        "$VENV_PYTHON" -m pytest tests/
        ;;
    "test-cov")
        echo -e "${GREEN}Running tests with coverage...${NC}"
        check_venv
        "$VENV_PYTHON" -m coverage run -m pytest tests/
        "$VENV_PYTHON" -m coverage report --show-missing
        ;;
    "clean")
        echo -e "${GREEN}Cleaning cache and build artifacts...${NC}"
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        rm -rf build dist *.egg-info .coverage htmlcov 2>/dev/null || true
        echo -e "${GREEN}Cleanup completed!${NC}"
        ;;
    "build")
        echo "Running full build pipeline..."
        check_venv
        errors=()

        echo "1. Checking formatting with ruff..."
        "$VENV_PYTHON" -m ruff format --check . || errors+=("Formatting check failed")

        echo "2. Linting with ruff..."
        "$VENV_PYTHON" -m ruff check . || errors+=("Linting failed")

        echo "3. Type checking with mypy..."
        "$VENV_PYTHON" -m mypy || errors+=("Type checking failed")

        echo "4. Testing with pytest..."
        "$VENV_PYTHON" -m pytest tests/ || errors+=("Tests failed")

        if [ ${#errors[@]} -gt 0 ]; then
            echo -e "${RED}\nBuild failed with the following errors:${NC}"
            for error in "${errors[@]}"; do
                echo -e "${RED}  - $error${NC}"
            done
            exit 1
        fi
        echo "Build completed successfully!"
        ;;

    "dev-setup")
        echo -e "${GREEN}Setting up development environment...${NC}"
        if [ ! -d ".venv" ]; then
            echo -e "${GREEN}Creating virtual environment...${NC}"
            python3 -m venv .venv
        fi
        echo -e "${GREEN}Python version: $("$VENV_PYTHON" --version)${NC}"
        "$VENV_PYTHON" -m pip install -r requirements-dev.txt
        echo -e "${GREEN}Development environment setup complete!${NC}"
        ;;
    "dev-check")
        echo -e "${GREEN}Running quick development check...${NC}"
        check_venv
        errors=()

        "$VENV_PYTHON" -m ruff format . || errors+=("Formatting failed")

        "$VENV_PYTHON" -m ruff check . --fix || errors+=("Linting failed")

        "$VENV_PYTHON" -m coverage run -m pytest tests/ || errors+=("Tests failed")

        "$VENV_PYTHON" -m coverage report

        if [ ${#errors[@]} -gt 0 ]; then
            echo -e "${RED}\nDevelopment check failed with the following errors:${NC}"
            for error in "${errors[@]}"; do
                echo -e "${RED}  - $error${NC}"
            done
            exit 1
        fi
        echo -e "${GREEN}Quick development check completed!${NC}"
        ;;
    "help")
        echo -e "${CYAN}Available commands:${NC}"
        echo "  run          - Run the application"
        echo "  install      - Install production dependencies"
        echo "  install-dev  - Install development dependencies"
        echo "  format       - Format code with ruff"
        echo "  check        - Check code with ruff"
        echo "  fix          - Fix code issues with ruff"
        echo "  check-file   - Check specific file (use --file parameter)"
        echo "  fix-file     - Fix specific file (use --file parameter)"
        echo "  mypy         - Type check main code"
        echo "  lint-all     - Run all linting checks"
        echo "  test         - Run tests"
        echo "  test-cov     - Run tests with coverage"
        echo "  clean        - Clean cache and build artifacts"
        echo "  build        - Run format, lint, type, and test checks"
        echo "  dev-setup    - Set up development environment"
        echo "  dev-check    - Quick development check (format + check + test)"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo "  ./scripts.sh format"
        echo "  ./scripts.sh check-file --file 'src/utils/logger.py'"
        echo "  ./scripts.sh build"
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo -e "${YELLOW}Use './scripts.sh help' to see available commands${NC}"
        exit 1
        ;;
esac