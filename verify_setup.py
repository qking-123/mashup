import sys
import subprocess


def check_python():
    v = sys.version_info
    print(f"✓ Python {v.major}.{v.minor}.{v.micro}")
    return v.major >= 3 and v.minor >= 7


def check_module(name):
    try:
        __import__(name.replace('-', '_'))
        print(f"✓ {name}")
        return True
    except ImportError:
        print(f"✗ {name} - run: pip install {name}")
        return False


def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✓ ffmpeg")
            return True
    except:
        pass
    print("✗ ffmpeg - install from ffmpeg.org")
    return False


def main():
    print("\nChecking setup...\n")
    
    checks = [
        check_python(),
        check_module('yt-dlp'),
        check_module('pydub'),
        check_module('flask'),
        check_ffmpeg()
    ]
    
    print()
    if all(checks):
        print("All good! Ready to go.\n")
    else:
        print("Fix the missing items above.\n")


if __name__ == "__main__":
    main()
