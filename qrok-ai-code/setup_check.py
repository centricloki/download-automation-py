"""
Setup verification script for the Playwright Download Automation Framework.

This script checks that all dependencies are installed and configured correctly.
Run this before using the framework to ensure everything is ready.

Usage:
    python setup_check.py
"""

import sys
import subprocess
from pathlib import Path


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_python_version():
    """Verify Python version is compatible."""
    print_section("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version too old. Please upgrade to Python 3.8+")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print_section("Dependency Check")
    
    dependencies = [
        "playwright",
        "aiosmtplib",
    ]
    
    optional = ["dotenv"]
    
    all_ok = True
    
    # Check required packages
    print("\nRequired packages:")
    for package in dependencies:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            all_ok = False
    
    # Check optional packages
    print("\nOptional packages:")
    for package in optional:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ⚠️  {package} - not installed (optional)")
    
    return all_ok


def check_playwright_browsers():
    """Verify Playwright browsers are installed."""
    print_section("Playwright Browser Check")
    
    try:
        result = subprocess.run(
            ["playwright", "show-installed-browsers"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Playwright browsers are installed")
            print(result.stdout[:500])  # Show first 500 chars
            return True
        else:
            print("⚠️  Playwright browsers may not be installed")
            print("   Run: playwright install chromium")
            return False
            
    except FileNotFoundError:
        print("❌ Playwright CLI not found")
        print("   Run: pip install playwright")
        print("   Then: playwright install chromium")
        return False
    except Exception as e:
        print(f"⚠️  Could not verify browsers: {e}")
        return False


def check_config_files():
    """Check if configuration files exist."""
    print_section("Configuration Files Check")
    
    required_files = [
        "config.py",
        "downloader.py",
        "utils.py",
        "email_notifier.py",
        "main.py",
        "requirements.txt",
    ]
    
    optional_files = [
        ".env",
        "sites.txt",
    ]
    
    all_ok = True
    
    print("\nRequired files:")
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - MISSING")
            all_ok = False
    
    print("\nOptional files:")
    for filename in optional_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ℹ️  {filename} - not present (copy from .example if needed)")
    
    return all_ok


def check_directories():
    """Verify required directories exist or can be created."""
    print_section("Directory Check")
    
    dirs = ["logs", "downloads"]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        
        if dir_path.exists():
            print(f"✅ Directory exists: {dir_name}/")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {dir_name}/")
            except Exception as e:
                print(f"❌ Failed to create {dir_name}/: {e}")
                return False
    
    return True


def check_email_config():
    """Warn if email configuration seems incomplete."""
    print_section("Email Configuration Check")
    
    try:
        from config import EMAIL_CONFIG
        
        required_keys = ["sender", "receiver", "smtp_server", "password"]
        missing = [key for key in required_keys if not EMAIL_CONFIG.get(key)]
        
        if missing:
            print("⚠️  Email configuration incomplete:")
            for key in missing:
                print(f"   - Missing: {key}")
            print("\n   Email notifications will be skipped until configured.")
            print("   Edit config.py or create .env file with credentials.")
            return False
        else:
            print("✅ Email configuration appears complete")
            
            # Additional check for Gmail App Password format
            password = EMAIL_CONFIG.get("password", "")
            if "gmail.com" in EMAIL_CONFIG.get("sender", "").lower():
                if len(password) < 10:
                    print("⚠️  Gmail password seems too short")
                    print("   Did you use an App Password? (16 characters)")
                    print("   Generate at: https://myaccount.google.com/apppasswords")
                    return False
                else:
                    print("✅ Gmail App Password format looks correct")
            
            return True
            
    except ImportError:
        print("❌ Could not import config.py")
        return False
    except Exception as e:
        print(f"⚠️  Error checking email config: {e}")
        return False


def check_site_configs():
    """Verify site configurations are valid."""
    print_section("Site Configuration Check")
    
    try:
        from config import SITES
        
        if not SITES:
            print("⚠️  No sites configured in config.py")
            print("   Add at least one site to the SITES dictionary")
            return False
        
        print(f"✅ Found {len(SITES)} configured site(s):\n")
        
        all_valid = True
        for site_key, site_config in SITES.items():
            print(f"  Site: {site_key}")
            
            # Check required fields
            required = ["url", "download_dir"]
            missing = [field for field in required if field not in site_config]
            
            if missing:
                print(f"    ❌ Missing fields: {missing}")
                all_valid = False
            else:
                print(f"    ✅ URL: {site_config['url'][:60]}...")
                print(f"    ✅ Download dir: {site_config['download_dir']}")
        
        return all_valid
        
    except ImportError:
        print("❌ Could not import config.py")
        return False
    except Exception as e:
        print(f"❌ Error in site configuration: {e}")
        return False


def run_full_check():
    """Run all setup checks and report results."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Playwright Download Automation - Setup Verification".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {}
    
    # Run all checks
    results["Python Version"] = check_python_version()
    results["Dependencies"] = check_dependencies()
    results["Playwright Browsers"] = check_playwright_browsers()
    results["Config Files"] = check_config_files()
    results["Directories"] = check_directories()
    results["Email Config"] = check_email_config()
    results["Site Configs"] = check_site_configs()
    
    # Summary
    print_section("Setup Check Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    print("\n" + "-" * 60)
    print(f"  Total: {passed}/{total} checks passed")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to start downloading.")
        print("\nNext steps:")
        print("  1. Run: python main.py --site delaware_business_licenses")
        print("  2. Check logs/downloader.log for detailed logs")
        print("  3. Run: python main.py to execute all sites")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Install browsers: playwright install chromium")
        print("  - Configure email in config.py or .env file")
    
    print()
    
    return passed == total


if __name__ == "__main__":
    success = run_full_check()
    sys.exit(0 if success else 1)
