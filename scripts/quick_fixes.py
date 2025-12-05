#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick fixes for critical issues identified in code review.

Run this script to apply immediate security and quality improvements.
"""

import sys
import codecs
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_config_security():
    """Check for placeholder values in config files."""
    print("🔍 Checking configuration security...")

    config_path = project_root / "config" / "config.env"
    if not config_path.exists():
        print("  ⚠️  config.env not found (OK if not set up yet)")
        return True

    content = config_path.read_text()

    dangerous_patterns = [
        ("your-secret-api-key-here", "API_KEY"),
        ("your-password-here", "PASSWORD"),
        ("changeme", "CHANGEME"),
    ]

    found_issues = []
    for pattern, name in dangerous_patterns:
        if pattern in content:
            found_issues.append(f"  ❌ Config contains placeholder: {name}")

    if found_issues:
        print("\n".join(found_issues))
        print("\n  ⚠️  SECURITY WARNING: Please change default values!")
        return False

    print("  ✅ Configuration looks secure")
    return True


def check_environment():
    """Check if running in production mode with proper settings."""
    print("\n🔍 Checking environment settings...")

    try:
        from src.core.config import get_settings
        settings = get_settings()

        issues = []

        # Check debug mode
        if settings.debug:
            issues.append("  ⚠️  DEBUG mode is enabled (should be False in production)")

        # Check API key
        if not settings.api_key or settings.api_key == "your-secret-api-key-here":
            issues.append("  ⚠️  API_KEY not set or using default value")

        # Check CORS (would need to check actual middleware config)
        print("  ℹ️  Remember to configure CORS origins for production")

        if issues:
            print("\n".join(issues))
            return False

        print("  ✅ Environment configuration looks good")
        return True

    except Exception as e:
        print(f"  ❌ Error checking environment: {e}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("yt_dlp", "Video downloader"),
    ]

    optional_packages = [
        ("faster_whisper", "AI subtitle generation (optional)"),
    ]

    missing_required = []
    missing_optional = []

    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: {description}")
        except ImportError:
            missing_required.append((package, description))
            print(f"  ❌ {package}: {description} - MISSING")

    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: {description}")
        except ImportError:
            missing_optional.append((package, description))
            print(f"  ⚠️  {package}: {description} - not installed")

    if missing_required:
        print("\n  ❌ Missing required packages! Run: pip install -r requirements.txt")
        return False

    if missing_optional:
        print("\n  ℹ️  Optional packages not installed. Install with:")
        print("     pip install faster-whisper")

    return True


def check_directory_structure():
    """Check if all required directories exist."""
    print("\n🔍 Checking directory structure...")

    required_dirs = [
        "config",
        "src",
        "src/api",
        "src/core",
        "src/sources",
        "src/processors",
        "data",
        "data/temp",
        "log",
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ⚠️  {dir_path}/ - creating...")
            full_path.mkdir(parents=True, exist_ok=True)
            all_exist = False

    if all_exist:
        print("  ✅ All directories present")
    else:
        print("  ℹ️  Created missing directories")

    return True


def check_gitignore():
    """Check if .gitignore is properly configured."""
    print("\n🔍 Checking .gitignore configuration...")

    gitignore_path = project_root / ".gitignore"

    if not gitignore_path.exists():
        print("  ❌ .gitignore not found!")
        return False

    content = gitignore_path.read_text()

    critical_patterns = [
        ("config/config.env", "Configuration file with secrets"),
        ("*.db", "Database files"),
        ("data/", "User data"),
        ("*.log", "Log files"),
    ]

    missing = []
    for pattern, description in critical_patterns:
        if pattern in content or pattern.replace("/", "\\") in content:
            print(f"  ✅ {pattern}: {description}")
        else:
            missing.append((pattern, description))
            print(f"  ⚠️  {pattern}: {description} - not in .gitignore")

    if missing:
        print("\n  ⚠️  Some sensitive files may not be excluded from git!")
        return False

    print("  ✅ .gitignore properly configured")
    return True


def generate_security_report():
    """Generate a security report."""
    print("\n" + "=" * 60)
    print("📋 SECURITY REPORT")
    print("=" * 60)

    report = []

    # Check for common security issues
    security_checks = [
        ("Configuration placeholders", check_config_security()),
        ("Environment settings", check_environment()),
        (".gitignore configuration", check_gitignore()),
    ]

    passed = sum(1 for _, result in security_checks if result)
    total = len(security_checks)

    print(f"\nPassed {passed}/{total} security checks")

    if passed < total:
        print("\n⚠️  SECURITY WARNINGS FOUND!")
        print("Please review the issues above and fix them before deploying.")
        return False

    print("\n✅ All security checks passed!")
    return True


def main():
    """Run all quick fix checks."""
    print("=" * 60)
    print("🔧 SmartNews Learn - Quick Fixes & Security Checks")
    print("=" * 60)

    checks = [
        ("Directory structure", check_directory_structure),
        ("Dependencies", check_dependencies),
        ("Security", generate_security_report),
    ]

    print("\nRunning checks...\n")

    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"\n❌ Error in {name} check: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Project looks good.")
        print("\nNext steps:")
        print("  1. Review CODE_REVIEW.md for detailed recommendations")
        print("  2. Run tests: python test_api.py")
        print("  3. Start server: python server.py")
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        print("\nRefer to CODE_REVIEW.md for detailed guidance.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
