import os
import shutil
import subprocess
import sys


APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(APP_DIR))
PROJECT_DIST = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
RELEASE_APP_DIR = os.path.join(PROJECT_ROOT, "release", "app")
SPEC_FILE = os.path.join(PROJECT_ROOT, "AutoClicker.spec")


def run(command):
    print("\n>", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main():
    requirements = os.path.join(APP_DIR, "requirements.txt")
    run([sys.executable, "-m", "pip", "install", "-r", requirements])

    for path in (BUILD_DIR, RELEASE_APP_DIR):
        if os.path.exists(path):
            shutil.rmtree(path)

    run([
        sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm",
        "--distpath", RELEASE_APP_DIR,
        "--workpath", BUILD_DIR,
        SPEC_FILE,
    ])

    exe = os.path.join(RELEASE_APP_DIR, "AutoClicker", "AutoClicker.exe")
    if not os.path.isfile(exe):
        raise SystemExit(f"Build finished but executable was not found: {exe}")
    print(f"\nBuild successful: {exe}")


if __name__ == "__main__":
    main()

