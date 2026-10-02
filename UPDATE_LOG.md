# Update Log - Drag and Drop Implementation

## Files Updated:

1. **requirements.txt**
   - Added: `tkinterdnd2` (for drag-and-drop support)

2. **README.md**
   - Updated Features section: Added "Graphical User Interface: Optional GUI with drag-and-drop support"
   - Updated Installation section: Added instructions to install tkinterdnd2 for GUI drag-and-drop
   - Updated Requirements section: Split into core converter (no external deps) and GUI drag-and-drop (requires tkinterdnd2)

3. **BUILD_EXE_INSTRUCTIONS.md**
   - Updated Prerequisites: Added step to install tkinterdnd2
   - Updated Step 1 (Install Dependencies): Changed to `pip install pyinstaller tkinterdnd2`
   - Updated Step 3 (Build the Executable): Added `--hidden-import=tkinterdnd2` to the pyinstaller command
   - Updated Section 4 (Locate the Generated Executable): Confirmed drag-and-drop functionality
   - Updated Section 5 (Distribute the Executable): Added "Drag and drop Python files onto it" to capabilities

4. **py_to_md_gui.py**
   - Added conditional import of tkinterdnd2 with fallback to standard Tk
   - Modified __init__ to conditionally register drop_target_register and dnd_bind
   - Rewrote on_drop method to use `self.root.tk.splitlist(event.data)` for proper file path handling
   - Updated update_drop_area_text calls to reflect DnD availability
   - Cleaned up unused imports (sys, pathlib.Path, ErrorType)

5. **py_to_md_gui.spec**
   - Confirmed hiddenimports includes 'tkinterdnd2'

## Verification:
- All instruction files updated to reflect tkinterdnd2 dependency
- Build instructions include necessary --hidden-import flag
- GUI implementation properly handles drag-and-drop with fallback when tkinterdnd2 not available
- Executable built with these instructions will support drag-and-drop functionality

## To Rebuild Executable:
Follow the updated instructions in BUILD_EXE_INSTRUCTIONS.md:
```bash
pip install pyinstaller tkinterdnd2
cd C:\Personal Projects\Py_to_MD
pyinstaller --onefile --windowed --hidden-import=tkinterdnd2 py_to_md_gui.py
```

The resulting `dist\py_to_md_gui.exe` will support drag-and-drop of Python files.