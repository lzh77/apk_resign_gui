"""
Build script for APK Resign GUI Application
This script automates the process of packaging the application using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_resources():
    """检查必要的资源文件是否存在"""
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print(f"警告: 图标文件 {icon_path} 不存在，这可能导致可执行文件没有自定义图标")
        return False
    return True


def run_pyinstaller():
    """Run PyInstaller with the spec file"""
    print("Starting build process with PyInstaller...")
    
    # 检查资源文件
    if not check_resources():
        print("资源文件缺失，构建可能失败或缺少图标")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "apk_resign_gui.spec"
        ], check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(e.stderr)
        sys.exit(1)


def build_dist_clean():
    """Clean previous builds and rebuild"""
    print("Cleaning previous build artifacts...")
    
    # Remove dist directory if it exists
    dist_path = Path("dist")
    if dist_path.exists():
        shutil.rmtree(dist_path)
        print("Removed old dist directory")
    
    # Remove build directory if it exists
    build_path = Path("build")
    if build_path.exists():
        shutil.rmtree(build_path)
        print("Removed old build directory")
    
    # Run PyInstaller
    run_pyinstaller()


def main():
    """Main function to handle build process"""
    print("APK Resign GUI - Build Script")
    print("="*40)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            build_dist_clean()
        elif sys.argv[1] == "help" or sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python build.py          - Build the application")
            print("  python build.py clean    - Clean previous builds and rebuild")
            print("  python build.py help     - Show this help message")
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use 'python build.py help' for usage information")
    else:
        # Just run PyInstaller normally
        run_pyinstaller()


if __name__ == "__main__":
    main()