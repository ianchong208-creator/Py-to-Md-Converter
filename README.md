# Python to Markdown Converter

A tool that converts Python source code to structured markdown format, making it easier for AI models and humans to understand code structure, particularly when dealing with broken or complex Python code.

## Features

- **Structured Output**: Converts Python code to well-organized markdown with clear sections
- **AI-Friendly Format**: Hierarchical structure that's easy for LLMs to parse and understand
- **Error Detection**: Gracefully handles syntax errors with clear reporting and context
- **Code Analysis**: Extracts and displays imports, functions, classes, constants, and variables
- **Command-Line Interface**: Simple CLI for easy integration into workflows
- **Graphical User Interface**: Optional GUI with drag-and-drop support for easy file conversion
- **Zero Core Dependencies**: Converter uses only Python standard library (requires Python 3.8+)

## Installation

No installation required for the command-line interface! The core converter uses only Python standard library modules.

For the graphical user interface with drag-and-drop support, you need to install the optional dependency:

```bash
# Make sure you have Python 3.8+
python --version

# Install tkinterdnd2 for drag-and-drop support in the GUI
pip install tkinterdnd2

# Download or copy the py_to_md_gui.py script
# Make it executable (optional)
chmod +x py_to_md_gui.py
```

## Usage

### Basic Usage

```bash
# Convert a Python file to markdown (output to stdout)
python py_to_md.py my_script.py

# Convert and save to a file
python py_to_md.py my_script.py -o my_script.md

# Read from stdin
cat my_script.py | python py_to_md.py
```

### Options

- `-o, --output FILE`: Write output to FILE instead of stdout
- `-v, --verbose`: Show detailed output including function descriptions and docstrings
- `--no-error-highlighting`: Disable error highlighting and reporting
- `--version`: Show version information

## Output Format

The converter produces markdown with the following sections:

### File Metadata
Basic information about the file being analyzed.

### Import Statements
Categorized into:
- **Standard Library**: Built-in Python modules
- **Third-Party Packages**: External libraries
- **Local Modules**: Project-specific imports

### Global Constants & Variables
- **Constants**: UPPER_CASE named variables
- **Variables**: Other variable assignments

### Class Definitions
Each class with:
- Inheritance information
- Methods (with signatures, return types, and decorators)
- Descriptions from docstrings

### Function Definitions
Standalone functions with:
- Parameter lists and return types
- Decorators
- Descriptions from docstrings

### Code Structure Summary
Statistics showing counts of different code elements.

### Syntax Analysis (when errors are present)
Clear error reporting with:
- Error type and message
- Problematic line number
- Context showing surrounding code
- Suggested fixes when possible

## Examples

### Simple Script

Input (`hello.py`):
```python
def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

Output:
```
# Python File Analysis: `hello.py`

## File Metadata
- **Filename**: `hello.py`
- **Size**: 89 bytes
- **Lines**: 5 lines
- **Status**: Successfully parsed

## Import Statements
*No imports found*

## Global Constants & Variables
*No constants or variables found*

## Class Definitions
*No classes found*

## Function Definitions
### `greet(name) -> str:`
- **Description**: Say hello to someone.

### `main() -> None:`

## Code Structure Summary
- **Classes**: 0
- **Functions**: 2
- **Imports**: 0
- **Constants**: 0
- **Variables**: 0
```

### With Error Detection

Input (`broken.py`):
```python
def calculate_total(items):
    total = 0
    for item in items
        total += item.price  # Missing colon after for statement
    return total
```

Output:
```
# Python File Analysis: `broken.py`

## File Metadata
- **Filename**: `broken.py`
- **Size**: 98 bytes
- **Lines**: 5 lines
- **Status**: Parsed with errors detected

## Import Statements
*No imports found*

## Global Constants & Variables
*No constants or variables found*

## Class Definitions
*No classes found*

## Function Definitions
### `calculate_total(items):`
- **Description**: None

## Code Structure Summary
- **Classes**: 0
- **Functions**: 1
- **Imports**: 0
- **Constants**: 0
- **Variables**: 0

## Syntax Analysis
### ⚠️ SyntaxError Detected
- **Message**: `invalid syntax`
- **Line**: 4
- **Context**:
  ```
   2: def calculate_total(items):
   3:     total = 0
   4:     for item in items
   5:         total += item.price  # Missing colon after for statement
   6:     return total
  ```
- **Suggested Fix**: Check for missing punctuation, mismatched brackets, or incorrect indentation
```

## How It Helps AI Models

The structured markdown output helps AI models by:

1. **Clear Hierarchy**: Code organization is explicit through markdown headings
2. **Reduced Complexity**: Boilerplate syntax is stripped away, revealing core structure
3. **Semantic Grouping**: Related elements (imports, functions, classes) are grouped together
4. **Error Visibility**: Syntax problems are clearly marked and explained
5. **Context Preservation**: Important details like function signatures and docstrings are maintained
6. **Predictable Format**: Consistent output structure allows LLMs to develop understanding patterns

## Requirements

- Python 3.8+ (for improved AST error messages and f-string debugging)
- Core converter: No external dependencies (uses only Python standard library)
- GUI drag-and-drop feature: Requires `tkinterdnd2` (install via `pip install tkinterdnd2`)

## License

MIT License - feel free to use, modify, and distribute as needed.