#!/usr/bin/env python
"""
Korame V1 Setup Script

Helps with initial setup and verification.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} done")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def check_python():
    """Check Python version."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 3.12+ required, found {version.major}.{version.minor}")
        return False


def check_venv():
    """Check if venv is activated."""
    print("🔍 Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment detected")
        return True
    else:
        print("⚠️  No virtual environment detected")
        print("   Run: python -m venv venv && source venv/bin/activate")
        return False


def check_ollama():
    """Check if Ollama is running."""
    print("🔍 Checking Ollama...")
    try:
        result = subprocess.run(
            'curl -s http://localhost:11434/api/tags | grep -q "models"',
            shell=True,
            capture_output=True
        )
        if result.returncode == 0:
            print("✓ Ollama is running")
            return True
        else:
            print("❌ Ollama is not responding")
            print("   Run: ollama serve")
            return False
    except Exception as e:
        print(f"⚠️  Could not check Ollama: {e}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print("\n🚀 Setting up Korame V1")
    print("=" * 50)

    # Check Python
    if not check_python():
        return False

    # Check venv
    venv_ok = check_venv()

    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -e .[dev]",
        "Installing dependencies"
    ):
        return False

    # Check Ollama
    check_ollama()

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Start Ollama: ollama serve")
    print("2. Pull models: ollama pull qwen2.5-coder:7b && ollama pull nomic-embed-text")
    print("3. Run tests: pytest tests/ -v")
    print("4. Start server: uvicorn app.main:app --reload")

    return True


def verify_installation():
    """Verify Korame is properly installed."""
    print("\n🔍 Verifying Korame installation...")
    print("=" * 50)

    # Check Python
    if not check_python():
        return False

    # Check venv
    check_venv()

    # Check Ollama
    check_ollama()

    # Check imports
    print("🔍 Checking imports...")
    try:
        from app.kernel import Agent, Provider, Registry, Task, Response
        from app.agents import RTEAgent, BaseAgent
        from app.providers import OllamaProvider
        from app.workflow import WorkflowEngine
        from app.memory import ConversationMemory
        from app.router import ModelRouter
        print("✓ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    print("\n✅ Installation verified!")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "setup":
            return install_dependencies()
        elif command == "verify":
            return verify_installation()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python scripts/setup.py [setup|verify]")
            return False
    else:
        # Interactive mode
        print("Korame V1 Setup")
        print("===============")
        print("1. setup   - Install dependencies and setup")
        print("2. verify  - Verify installation")
        print("3. quit    - Exit")

        choice = input("\nChoose an option (1-3): ").strip()

        if choice == "1":
            return install_dependencies()
        elif choice == "2":
            return verify_installation()
        else:
            return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

