# How to Create an Executable (.exe) File

This guide explains how to convert the Python GUI application into a standalone executable file that can be run on Windows without requiring Python to be installed.

## Prerequisites

1. Python 3.8+ installed on your system
2. PyInstaller installed: `pip install pyinstaller`
3. tkinterdnd2 installed (for drag-and-drop support): `pip install tkinterdnd2`

## Step-by-Step Instructions

### 1. Install Dependencies
Open Command Prompt or PowerShell and run:
```bash
pip install pyinstaller tkinterdnd2
```

### 2. Navigate to the Project Directory
```bash
cd C:\Personal Projects\Py_to_MD
```

### 3. Build the Executable
Run PyInstaller with the following command to create a single-file executable:
```bash
pyinstaller --onefile --windowed --hidden-import=tkinterdnd2 py_to_md_gui.py
```

### Explanation of Flags:
- `--onefile`: Bundles everything into a single executable file
- `--windowed`: Prevents a console window from appearing (GUI-only application)
- `py_to_md_gui.py`: The script to convert

### 4. Locate the Generated Executable
After the build completes (may take a few minutes), you'll find the executable in:
```
C:\Personal Projects\Py_to_MD\dist\py_to_md_gui.exe
```

### 5. Distribute the Executable
The `py_to_md_gui.exe` file in the `dist` folder is your standalone application. You can:
- Copy it to any Windows computer
- Drag and drop Python files onto it
- Use the browse button to select files
- No Python installation required on the target machine

## Optional: Customizing the Executable

### Add an Icon
To add a custom icon to your executable:
```bash
pyinstaller --onefile --windowed --icon=your_icon.ico py_to_md_gui.py
```
Replace `your_icon.ico` with the path to your icon file.

### Specify Version Information
You can create a version file and include it:
```bash
pyinstaller --onefile --windowed --version-file=version.txt py_to_md_gui.py
```

### Reduce False Positive Virus Flags
Some antivirus software may flag PyInstaller-generated executables. To reduce this:
1. Sign your executable with a code signing certificate
2. Submit false positive reports to antivirus vendors
3. Use UPX packing (may increase false positives in some cases):
   ```bash
   pyinstaller --onefile --windowed --upx-dir=/path/to/upx py_to_md_gui.py
   ```

## Testing the Executable

1. Navigate to the `dist` folder
2. Double-click `py_to_md_gui.exe` to launch the application
3. Use the Browse button to select a Python file
4. Click "Convert to Markdown" to see the results
5. Use Save or Copy buttons to export the markdown output

## Troubleshooting

### Missing DLL Errors
If you encounter missing DLL errors on the target machine:
1. Install the Microsoft Visual C++ Redistributable package
2. Ensure all required runtime libraries are present

### Antivirus False Positives
If antivirus software flags the executable:
1. This is common with PyInstaller-generated files
2. Submit the file to the antivirus vendor as a false positive
3. Consider code signing for distribution

## Alternative: Directory-Based Build
If you prefer to see all the bundled files or encounter issues with the single-file approach:
```bash
pyinstaller --windowed py_to_md_gui.py
```
This creates a `build` and `dist` folder with the executable and its dependencies.

The executable will be in `dist\py_to_md_gui\py_to_md_gui.exe`

## Notes

- The first run of the executable may take a few seconds to start as it extracts bundled files
- File size will be approximately 10-15 MB due to the bundled Python interpreter
- Updates require rebuilding and redistributing the executable
- For best results, build on the same Windows version you intend to run it on