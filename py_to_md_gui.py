#!/usr/bin/env python3
"""
Python to Markdown Converter GUI
A graphical interface for converting Python source code to structured markdown format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
import os
import threading

# Try to import tkinterdnd2 for drag-and-drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    TkinterDnD = tk.Tk  # fallback
    DND_FILES = None

# Import the converter logic from our original script
from py_to_md import PythonToMarkdownConverter


class PythonToMarkdownGUI:
    """Main GUI application class"""

    def __init__(self, root):
        self.root = root
        self.root.title("Python to Markdown Converter")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Variables
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.verbose_mode = tk.BooleanVar(value=False)
        self.highlight_errors = tk.BooleanVar(value=True)
        self.is_converting = False

        # Create the converter instance
        self.converter = PythonToMarkdownConverter()

        # Setup the GUI
        self.setup_gui()

        # Register drag and drop if available
        if TKDND_AVAILABLE and DND_FILES:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
            self.update_drop_area_text("Drag Python file here\nor click Browse above")
        else:
            self.update_drop_area_text("Drag & drop not available\nclick Browse above")

    def setup_gui(self):
        """Setup the graphical user interface"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Output text area

        # Title
        title_label = ttk.Label(main_frame, text="Python to Markdown Converter",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Input file section
        ttk.Label(main_frame, text="Input Python File:").grid(row=1, column=0, sticky=tk.W, pady=5)

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_file_path,
                                    font=("Arial", 10))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        browse_btn = ttk.Button(input_frame, text="Browse...",
                               command=self.browse_input_file)
        browse_btn.grid(row=0, column=1)

        # Drag and drop area
        ttk.Label(main_frame, text="Or drag & drop Python file here:").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))

        self.drop_area = tk.Label(main_frame, text="Drag Python file here\nor click Browse above",
                                 relief="sunken", bg="#f0f0f0", height=3,
                                 font=("Arial", 9))
        self.drop_area.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.drop_area.bind("<Button-1>", lambda e: self.browse_input_file())

        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)

        ttk.Checkbutton(options_frame, text="Verbose mode (show descriptions and docstrings)",
                       variable=self.verbose_mode).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Highlight syntax errors",
                       variable=self.highlight_errors).grid(row=1, column=0, sticky=tk.W, pady=2)

        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert to Markdown",
                                     command=self.start_conversion)
        self.convert_btn.grid(row=5, column=0, columnspan=3, pady=15)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to convert")
        self.status_label.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=2)

        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Markdown Output", padding="5")
        output_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                    font=("Consolas", 10))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Output buttons
        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        output_btn_frame.columnconfigure(0, weight=1)
        output_btn_frame.columnconfigure(1, weight=1)

        self.save_btn = ttk.Button(output_btn_frame, text="Save Markdown...",
                                  command=self.save_output, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.copy_btn = ttk.Button(output_btn_frame, text="Copy to Clipboard",
                                  command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_btn.grid(row=0, column=1, sticky=tk.E)

        # Clear button
        clear_btn = ttk.Button(main_frame, text="Clear", command=self.clear_all)
        clear_btn.grid(row=9, column=0, columnspan=3, pady=10)

    def browse_input_file(self):
        """Open file dialog to select input Python file"""
        filename = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            defaultextension=".py"
        )
        if filename:
            self.input_file_path.set(filename)
            self.update_drop_area_text(f"Selected: {os.path.basename(filename)}")

    def update_drop_area_text(self, text):
        """Update the drag and drop area text"""
        self.drop_area.config(text=text)

    def on_drop(self, event):
        """Handle drag and drop event"""
        try:
            # Use Tk's splitlist to properly handle curly braces and spaces
            file_list = self.root.tk.splitlist(event.data)
            if not file_list:
                self.update_drop_area_text("No files dropped")
                return
            # Take the first file that is a .py file
            file_path = None
            for f in file_list:
                if f.lower().endswith('.py') and os.path.isfile(f):
                    file_path = f
                    break
            if file_path is None:
                # If no .py file, maybe show first file anyway? but we require .py
                self.update_drop_area_text("Please drop a .py file")
                return
            self.input_file_path.set(file_path)
            self.update_drop_area_text(f"Selected: {os.path.basename(file_path)}")
        except Exception as e:
            self.update_drop_area_text(f"Drop error: {e}")

    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if self.is_converting:
            return

        input_file = self.input_file_path.get().strip()
        if not input_file:
            messagebox.showwarning("Warning", "Please select a Python file first.")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"File not found: {input_file}")
            return

        # Disable UI during conversion
        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Converting...")
        self.output_text.delete(1.0, tk.END)

        # Run conversion in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.perform_conversion, args=(input_file,))
        thread.daemon = True
        thread.start()

    def perform_conversion(self, input_file):
        """Perform the actual conversion (runs in separate thread)"""
        try:
            # Update converter settings based on GUI options
            self.converter = PythonToMarkdownConverter(
                show_details=self.verbose_mode.get(),
                highlight_errors=self.highlight_errors.get()
            )

            # Perform conversion
            markdown_output = self.converter.convert_file(input_file)

            # Update GUI in main thread
            self.root.after(0, self.conversion_complete, markdown_output, None)

        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}"
            self.root.after(0, self.conversion_error, error_msg)

    def conversion_complete(self, markdown_output, error=None):
        """Called when conversion completes successfully"""
        self.is_converting = False
        self.progress.stop()
        self.convert_btn.config(state=tk.NORMAL)

        if error:
            self.status_label.config(text="Conversion failed")
            messagebox.showerror("Conversion Error", error)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {error}")
        else:
            self.status_label.config(text="Conversion completed successfully")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, markdown_output)
            self.save_btn.config(state=tk.NORMAL)
            self.copy_btn.config(state=tk.NORMAL)

    def conversion_error(self, error_msg):
        """Called when conversion encounters an error"""
        self.is_converting = False
        self.progress.stop()
        self.convert_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Conversion failed")
        messagebox.showerror("Conversion Error", error_msg)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Error: {error_msg}")

    def save_output(self):
        """Save the markdown output to a file"""
        markdown_content = self.output_text.get(1.0, tk.END).strip()
        if not markdown_content or markdown_content.startswith("Error:"):
            messagebox.showwarning("Warning", "No valid markdown output to save.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Markdown File",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".md",
            initialfile="output.md"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                self.status_label.config(text=f"Saved to {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Markdown saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")

    def copy_to_clipboard(self):
        """Copy the markdown output to clipboard"""
        markdown_content = self.output_text.get(1.0, tk.END).strip()
        if not markdown_content or markdown_content.startswith("Error:"):
            messagebox.showwarning("Warning", "No valid markdown output to copy.")
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(markdown_content)
            self.root.update()  # Keeps clipboard content after window closes
            self.status_label.config(text="Copied to clipboard")
            messagebox.showinfo("Success", "Markdown copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard:\n{str(e)}")

    def clear_all(self):
        """Clear all fields and reset the interface"""
        self.input_file_path.set("")
        self.output_file_path.set("")
        self.verbose_mode.set(False)
        self.highlight_errors.set(True)
        if TKDND_AVAILABLE and DND_FILES:
            self.update_drop_area_text("Drag Python file here\nor click Browse above")
        else:
            self.update_drop_area_text("Drag & drop not available\nclick Browse above")
        self.output_text.delete(1.0, tk.END)
        self.save_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Ready to convert")


def main():
    """Main entry point for the GUI application"""
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        # Show a warning that drag-and-drop is not available
        # We'll let the GUI handle it via the drop area text
    app = PythonToMarkdownGUI(root)

    # Handle window closing properly
    def on_closing():
        if app.is_converting:
            if messagebox.askokcancel("Quit", "Conversion is in progress. Quit anyway?"):
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()