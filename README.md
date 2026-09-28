# AutoClicker

AutoClicker is a Windows desktop app for creating mouse-click sequences and assigning global hotkeys.

## Download

Download the latest Windows installer from the [Releases](../../releases) page. Version 3.2.0 supports assigning each click position to an individual key (A–Z and F1–F12). Pressing a key runs its assigned positions in order. The cursor returns to its starting position after the macro ends or stops.

## Features

- Multiple profiles and global hotkeys
- Per-action screen coordinates and mouse button (left, right, middle)
- Per-action hotkeys (A–Z and F1–F12)
- Multiple clicks, delays, repeats, and infinite loops
- Emergency stop with Esc
- System tray, import/export, and Windows startup options

## Build from source

Requires Python 3 and Windows. From the project root:

```powershell
python -m pip install -r dist/AutoClicker/requirements.txt
python dist/run_autoclicker.py
```

Build a Windows app bundle with PyInstaller:

```powershell
python -m PyInstaller --noconfirm --distpath release/app --workpath build AutoClicker.spec
```

Create the installer with Inno Setup 6:

```powershell
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' installer/AutoClicker.iss.txt
```

The Inno Setup script reads the bundle from `release/app/AutoClicker` and writes the installer to `release/`.

