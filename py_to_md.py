"""
Python to Markdown Converter
Converts Python source code to structured markdown format.
"""

import ast
import sys
from enum import Enum
from typing import List, Optional, Set, Dict
import keyword
import builtins


class ErrorType(Enum):
    """Types of errors that can be detected during parsing."""
    SYNTAX_ERROR = "SyntaxError"
    INDENTATION_ERROR = "IndentationError"
    OTHER_ERROR = "OtherError"


class PythonToMarkdownConverter:
    """Converts Python source code to structured markdown format."""

    def __init__(self, show_details: bool = False, highlight_errors: bool = True):
        """
        Initialize the converter.

        Args:
            show_details: Whether to show detailed descriptions and docstrings
            highlight_errors: Whether to highlight and report syntax errors
        """
        self.show_details = show_details
        self.highlight_errors = highlight_errors

    def convert_file(self, file_path: str) -> str:
        """
        Convert a Python file to markdown.

        Args:
            file_path: Path to the Python file to convert

        Returns:
            Markdown formatted string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.convert_string(content, file_path)
        except FileNotFoundError:
            return f"# Error: File not found - {file_path}\n"
        except Exception as e:
            return f"# Error reading file: {str(e)}\n"

    def convert_string(self, content: str, filename: str = "<string>") -> str:
        """
        Convert Python source code string to markdown.

        Args:
            content: Python source code as string
            filename: Name of the file (for display purposes)

        Returns:
            Markdown formatted string
        """
        # Try to parse the code
        try:
            tree = ast.parse(content)
            has_errors = False
            error_info = None
        except SyntaxError as e:
            tree = None
            has_errors = True
            error_info = {
                'type': ErrorType.SYNTAX_ERROR,
                'message': str(e),
                'line': e.lineno,
                'text': e.text
            }
        except IndentationError as e:
            tree = None
            has_errors = True
            error_info = {
                'type': ErrorType.INDENTATION_ERROR,
                'message': str(e),
                'line': e.lineno,
                'text': e.text
            }
        except Exception as e:
            tree = None
            has_errors = True
            error_info = {
                'type': ErrorType.OTHER_ERROR,
                'message': str(e),
                'line': getattr(e, 'lineno', None),
                'text': getattr(e, 'text', None)
            }

        # Start building markdown output
        markdown_lines = []

        # File header
        markdown_lines.append(f"# Python File Analysis: `{filename}`")
        markdown_lines.append("")

        # File metadata
        lines_count = len(content.splitlines())
        size_bytes = len(content.encode('utf-8'))
        status = "Successfully parsed" if not has_errors else "Parsed with errors detected"

        markdown_lines.append("## File Metadata")
        markdown_lines.append(f"- **Filename**: `{filename}`")
        markdown_lines.append(f"- **Size**: {size_bytes} bytes")
        markdown_lines.append(f"- **Lines**: {lines_count} lines")
        markdown_lines.append(f"- **Status**: {status}")
        markdown_lines.append("")

        if has_errors and self.highlight_errors and error_info:
            # Add syntax analysis section for errors
            markdown_lines.extend(self._format_error_analysis(error_info, content))
            return "\n".join(markdown_lines)

        if tree is None:
            # If we couldn't parse at all, just return what we have
            return "\n".join(markdown_lines)

        # Analyze the AST
        analyzer = PythonASTAnalyzer(
            show_details=self.show_details,
            highlight_errors=self.highlight_errors
        )
        analyzer.visit(tree)

        # Add import statements
        markdown_lines.extend(self._format_imports(analyzer.imports))

        # Add global constants and variables
        markdown_lines.extend(self._format_globals(analyzer.constants, analyzer.variables))

        # Add class definitions
        markdown_lines.extend(self._format_classes(analyzer.classes))

        # Add function definitions
        markdown_lines.extend(self._format_functions(analyzer.functions))

        # Add code structure summary
        markdown_lines.extend(self._format_summary(
            len(analyzer.classes),
            len(analyzer.functions),
            len(analyzer.imports['Standard Library']) +
            len(analyzer.imports['Third-Party Packages']) +
            len(analyzer.imports['Local Modules']),
            len(analyzer.constants),
            len(analyzer.variables)
        ))

        return "\n".join(markdown_lines)

    def _format_imports(self, imports: Dict[str, Set[str]]) -> List[str]:
        """Format import statements section."""
        lines = ["## Import Statements"]

        has_imports = False
        for category, imp_list in imports.items():
            if imp_list:
                has_imports = True
                lines.append(f"- **{category}**:")
                for imp in sorted(imp_list):
                    lines.append(f"  - `{imp}`")

        if not has_imports:
            lines.append("*No imports found*")
        else:
            # Add blank line after imports section
            lines.append("")

        return lines

    def _format_globals(self, constants: Dict[str, str], variables: Dict[str, str]) -> List[str]:
        """Format global constants and variables section."""
        lines = ["## Global Constants & Variables"]

        has_globals = False

        if constants:
            has_globals = True
            lines.append("- **Constants**: UPPER_CASE named variables")
            for name, value in sorted(constants.items()):
                lines.append(f"  - `{name}` = {value}")

        if variables:
            has_globals = True
            lines.append("- **Variables**: Other variable assignments")
            for name, value in sorted(variables.items()):
                lines.append(f"  - `{name}` = {value}")

        if not has_globals:
            lines.append("*No constants or variables found*")
        else:
            lines.append("")  # Blank line after section

        return lines

    def _format_classes(self, classes: List[Dict]) -> List[str]:
        """Format class definitions section."""
        if not classes:
            return ["## Class Definitions", "*No classes found*", ""]

        lines = ["## Class Definitions"]
        for cls in classes:
            lines.append(f"### `class {cls['name']}`{cls.get('inheritance', '')}:")
            if self.show_details and cls.get('docstring'):
                lines.append(f"- **Description**: {cls['docstring']}")

            if cls.get('methods'):
                lines.append("- **Methods**:")
                for method in cls['methods']:
                    sig = self._format_signature(method['args'], method.get('returns'))
                    decorators = f" {' '.join(method['decorators'])}" if method.get('decorators') else ""
                    lines.append(f"  - `{method['name']}{sig}`{decorators}")
                    if self.show_details and method.get('docstring'):
                        lines.append(f"    - {method['docstring']}")
            else:
                lines.append("- **Methods**: *None*")

            lines.append("")  # Blank line between classes

        # Remove extra blank line at end and add one
        if lines[-1] == "":
            lines.pop()
        lines.append("")
        return lines

    def _format_functions(self, functions: List[Dict]) -> List[str]:
        """Format function definitions section."""
        if not functions:
            return ["## Function Definitions", "*No functions found*", ""]

        lines = ["## Function Definitions"]
        for func in functions:
            sig = self._format_signature(func['args'], func.get('returns'))
            decorators = f" {' '.join(func['decorators'])}" if func.get('decorators') else ""
            lines.append(f"### `{func['name']}{sig}`{decorators}:")
            if self.show_details and func.get('docstring'):
                lines.append(f"- **Description**: {func['docstring']}")
            elif not self.show_details:
                lines.append("- **Description**: None")
            lines.append("")  # Blank line between functions

        # Remove extra blank line at end and add one
        if lines[-1] == "":
            lines.pop()
        lines.append("")
        return lines

    def _format_summary(self, class_count: int, func_count: int, import_count: int,
                       const_count: int, var_count: int) -> List[str]:
        """Format code structure summary section."""
        lines = [
            "## Code Structure Summary",
            f"- **Classes**: {class_count}",
            f"- **Functions**: {func_count}",
            f"- **Imports**: {import_count}",
            f"- **Constants**: {const_count}",
            f"- **Variables**: {var_count}",
            ""  # Blank line after section
        ]
        return lines

    def _format_error_analysis(self, error_info: dict, content: str) -> List[str]:
        """Format syntax error analysis section."""
        lines = []

        error_type = error_info['type'].value
        message = error_info['message']
        line_num = error_info['line']
        text = error_info['text']

        lines.extend([
            "## Syntax Analysis",
            f"### ⚠️ {error_type} Detected",
            f"- **Message**: `{message}`",
            f"- **Line**: {line_num}"
        ])

        if text is not None:
            # Show context around the error
            content_lines = content.splitlines()
            start_line = max(0, line_num - 3)  # Show 2 lines before
            end_line = min(len(content_lines), line_num + 2)  # Show 2 lines after

            lines.append("- **Context**:")
            lines.append("  ```")
            for i in range(start_line, end_line):
                line_num_actual = i + 1
                marker = ">>> " if line_num_actual == line_num else "    "
                lines.append(f"  {marker}{line_num_actual:3}: {content_lines[i]}")
            lines.append("  ```")

        lines.extend([
            "- **Suggested Fix**: Check for missing punctuation, mismatched brackets, or incorrect indentation",
            ""  # Blank line after section
        ])

        return lines

    def _format_signature(self, args: List[str], returns: Optional[str]) -> str:
        """Format a function signature."""
        args_str = ", ".join(args) if args else ""
        returns_str = f" -> {returns}" if returns else ""
        return f"({args_str}){returns_str}"


class PythonASTAnalyzer(ast.NodeVisitor):
    """AST visitor to extract information from Python code."""

    def __init__(self, show_details: bool = False, highlight_errors: bool = True):
        self.show_details = show_details
        self.highlight_errors = highlight_errors

        # Standard library modules (common ones)
        self.stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools', 'functools',
            're', 'math', 'random', 'string', 'collections', 'heapq', 'bisect',
            'copy', 'pprint', 'io', 'tempfile', 'glob', 'shutil', 'subprocess',
            'threading', 'multiprocessing', 'queue', 'socket', 'ssl', 'http',
            'urllib', 'html', 'xml', 'csv', 'sqlite3', 'pickle', 'shelve',
            'hashlib', 'hmac', 'secrets', 'asyncio', 'concurrent', 'logging',
            'unittest', 'test', 'argparse', 'getopt', 'optparse', 'configparser',
            'plistlib', 'mailbox', 'mailcap', 'mimetypes', 'base64', 'binascii',
            'quopri', 'uu', 'struct', 'binhex', 'xc85', 'xdrlib', 'pitfalls'
        }

        # Built-in functions and types
        self.builtins = set(dir(builtins))

        # Keywords
        self.keywords = set(keyword.kwlist)

        # Storage for extracted information
        self.imports = {
            'Standard Library': set(),
            'Third-Party Packages': set(),
            'Local Modules': set()
        }
        self.constants = {}  # UPPER_CASE variables
        self.variables = {}  # other variables
        self.classes = []    # class definitions
        self.functions = []  # function definitions

        # Track current context
        self.current_class = None
        self.current_function = None

        # Track parent nodes for assignments
        self.parent_map = {}

    def visit(self, node):
        """Visit a node and set up parent tracking."""
        for child in ast.iter_child_nodes(node):
            self.parent_map[child] = node
        super().visit(node)

    def visit_Import(self, node):
        """Handle import statements."""
        for alias in node.names:
            module_name = alias.name.split('.')[0]  # Get top-level module
            self._categorize_import(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Handle from ... import ... statements."""
        if node.module:
            module_name = node.module.split('.')[0]  # Get top-level module
            self._categorize_import(module_name)
        self.generic_visit(node)

    def _categorize_import(self, module_name: str):
        """Categorize an import as stdlib, third-party, or local."""
        if module_name in self.stdlib_modules:
            self.imports['Standard Library'].add(module_name)
        elif module_name in self.builtins or module_name in self.keywords:
            # Built-in or keyword, treat as stdlib for simplicity
            self.imports['Standard Library'].add(module_name)
        else:
            # Heuristic: if it contains dots or common third-party patterns,
            # or if it's not obviously stdlib, treat as third-party
            # This is a simplification - in reality we'd need to check sys.path or try to import
            if '.' in module_name or any(common in module_name.lower() for common in
                                       ['django', 'flask', 'numpy', 'pandas', 'requests',
                                        'matplotlib', 'scipy', 'sklearn', 'tensorflow',
                                        'torch', 'keras', 'bs4', 'lxml', 'pytest']):
                self.imports['Third-Party Packages'].add(module_name)
            else:
                # Assume local module if we can't categorize it
                self.imports['Local Modules'].add(module_name)

    def visit_Assign(self, node):
        """Handle assignment statements."""
        # Check if this is a module-level assignment
        parent = self.parent_map.get(node)
        if isinstance(parent, ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Try to get the value if it's a simple constant
                    value = self._get_simple_value(node.value)
                    if var_name.isupper() and len(var_name) > 1:
                        # Likely a constant
                        self.constants[var_name] = value
                    else:
                        # Regular variable
                        self.variables[var_name] = value
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle function definitions."""
        func_info = self._extract_function_info(node)

        # Check if this is a method (inside a class) or standalone function
        if self.current_class is not None:
            # It's a method
            if 'methods' not in self.current_class:
                self.current_class['methods'] = []
            self.current_class['methods'].append(func_info)
        else:
            # It's a standalone function
            self.functions.append(func_info)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Handle class definitions."""
        class_info = self._extract_class_info(node)

        # Save current context
        prev_class = self.current_class
        self.current_class = class_info

        # Process the class body
        self.generic_visit(node)

        # Restore context
        self.current_class = prev_class

        # Add to classes list
        self.classes.append(class_info)

    def _extract_function_info(self, node: ast.FunctionDef) -> dict:
        """Extract information from a function definition."""
        # Get function name
        name = node.name

        # Get arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        # Handle *args
        if node.args.vararg:
            args.append('*' + node.args.vararg.arg)
        # Handle **kwargs
        if node.args.kwarg:
            args.append('**' + node.args.kwarg.arg)

        # Get return type annotation (if any)
        returns = None
        if node.returns:
            returns = self._annotation_to_string(node.returns)

        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._annotation_to_string(decorator))

        # Get docstring
        docstring = ast.get_docstring(node)

        return {
            'name': name,
            'args': args,
            'returns': returns,
            'decorators': decorators,
            'docstring': docstring
        }

    def _extract_class_info(self, node: ast.ClassDef) -> dict:
        """Extract information from a class definition."""
        # Get class name
        name = node.name

        # Get inheritance
        inheritance = ""
        if node.bases:
            base_names = []
            for base in node.bases:
                base_names.append(self._annotation_to_string(base))
            if base_names:
                inheritance = f"({', '.join(base_names)})"

        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._annotation_to_string(decorator))

        # Get docstring
        docstring = ast.get_docstring(node)

        return {
            'name': name,
            'inheritance': inheritance,
            'decorators': decorators,
            'docstring': docstring,
            'methods': []  # Will be populated as we visit methods
        }

    def _annotation_to_string(self, node) -> str:
        """Convert an AST node to a string representation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Attribute):
            value_str = self._annotation_to_string(node.value)
            return f"{value_str}.{node.attr}" if value_str else node.attr
        else:
            # For complex annotations, just show the type
            return type(node).__name__.replace('ast.', '')

    def _get_simple_value(self, node) -> str:
        """Try to extract a simple constant value from a node."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.List):
            elts = [self._get_simple_value(elt) for elt in node.elts]
            return f"[{', '.join(elts)}]"
        elif isinstance(node, ast.Tuple):
            elts = [self._get_simple_value(elt) for elt in node.elts]
            return f"({', '.join(elts)})"
        elif isinstance(node, ast.Dict):
            keys = [self._get_simple_value(k) for k in node.keys]
            values = [self._get_simple_value(v) for v in node.values]
            items = [f"{k}: {v}" for k, v in zip(keys, values)]
            return f"{{{', '.join(items)}}}"
        elif isinstance(node, ast.Set):
            elts = [self._get_simple_value(elt) for elt in node.elts]
            return f"{{{', '.join(elts)}}}"
        else:
            # For complex expressions, return a placeholder
            return "<complex expression>"


def main():
    """Main entry point for the command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert Python source code to structured markdown format."
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Python file to convert (if omitted, reads from stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Write output to FILE instead of stdout'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output including function descriptions and docstrings'
    )
    parser.add_argument(
        '--no-error-highlighting',
        action='store_true',
        help='Disable error highlighting and reporting'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )

    args = parser.parse_args()

    if args.version:
        print("Python to Markdown Converter v1.0")
        return

    converter = PythonToMarkdownConverter(
        show_details=args.verbose,
        highlight_errors=not args.no_error_highlighting
    )

    if args.file:
        # Convert file
        markdown_output = converter.convert_file(args.file)
    else:
        # Convert from stdin
        content = sys.stdin.read()
        markdown_output = converter.convert_string(content, "<stdin>")

    # Output to file or stdout
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        print(f"Output written to {args.output}")
    else:
        print(markdown_output)


if __name__ == "__main__":
    main()