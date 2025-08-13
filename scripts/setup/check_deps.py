#!/usr/bin/env python3
"""
Dependency checker for VideoCraft project.
Verifies that all required packages are installed and compatible.
"""

import sys
import importlib.util

def check_package(package_name, min_version=None):
    """Check if a package is installed and optionally verify minimum version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        
        print(f"✅ {package_name}: {version}")
        
        if min_version and hasattr(module, '__version__'):
            from packaging import version as pkg_version
            if pkg_version.parse(version) < pkg_version.parse(min_version):
                print(f"⚠️  Warning: {package_name} {version} is below minimum required {min_version}")
                return False
        
        return True
    except ImportError:
        print(f"❌ {package_name}: Not installed")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: Error checking version ({e})")
        return False

def main():
    """Main dependency check function."""
    print("🔍 VideoCraft Dependency Check")
    print("=" * 40)
    
    # Core dependencies
    dependencies = [
        ("torch", "2.6.0"),
        ("torchaudio", "2.5.1"),
        ("torchvision", "0.23.0"),
        ("numpy", "2.0.2"),
        ("transformers", "4.48.0"),
        ("streamlit", None),
        ("opencv-python", None),  # opencv-python shows as cv2
        ("moviepy", None),
        ("librosa", None),
        ("pandas", None),
        ("PIL", None),  # Pillow shows as PIL
        ("yaml", None),  # PyYAML shows as yaml
    ]
    
    # Special cases for package name mapping
    package_map = {
        "opencv-python": "cv2",
        "PIL": "PIL",
        "yaml": "yaml"
    }
    
    all_ok = True
    
    for package, min_ver in dependencies:
        actual_package = package_map.get(package, package)
        if not check_package(actual_package, min_ver):
            all_ok = False
    
    print("\n" + "=" * 40)
    
    if all_ok:
        print("🎉 All dependencies are installed and compatible!")
        print("You can run: streamlit run main.py")
    else:
        print("⚠️  Some dependencies are missing or incompatible.")
        print("Run: python setup.py")
        sys.exit(1)

if __name__ == "__main__":
    try:
        import packaging
    except ImportError:
        print("Installing packaging module for version checking...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "packaging"])
        import packaging
    
    main()
