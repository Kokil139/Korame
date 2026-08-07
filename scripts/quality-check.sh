#!/bin/bash

# Quality check script for development
# Run all checks before committing

set -e

echo "🔍 Korame Quality Check"
echo "======================="
echo ""

echo "📝 Formatting with Black..."
black app/ tests/
echo "✓ Black done"
echo ""

echo "🚨 Linting with Flake8..."
flake8 app/ tests/ || echo "⚠️  Some linting issues found"
echo "✓ Flake8 done"
echo ""

echo "🔐 Type checking with MyPy..."
mypy app/ || echo "⚠️  Some type issues found"
echo "✓ MyPy done"
echo ""

echo "🧪 Running tests..."
pytest tests/ -v --cov=app --cov-report=term-missing
echo "✓ Tests done"
echo ""

echo "✅ Quality check complete!"

