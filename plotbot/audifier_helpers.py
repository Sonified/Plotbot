from tkinter import Tk, filedialog
import os
import ipywidgets as widgets
from IPython.display import display
from datetime import datetime
from scipy.io import wavfile

def open_directory(directory):
    """Open directory in system file explorer."""
    if os.name == 'nt':  # For Windows
        os.startfile(directory)
    elif os.name == 'posix':  # For macOS and Linux
        os.system(f'open "{directory}"')

def show_directory_button(directory):
    """Display a button that opens the specified directory."""
    button = widgets.Button(description="Show Directory")
    def on_button_click(b):
        open_directory(directory)
    button.on_click(on_button_click)
    display(button)

def show_file_buttons(file_paths):
    """Display buttons to open specified files."""
    for label, file_path in file_paths.items():
        button = widgets.Button(description=f"Open {label}")
        def on_button_click(b, path=file_path):
            if os.name == 'nt':  # For Windows
                os.startfile(path)
            elif os.name == 'posix':  # For macOS and Linux
                os.system(f'open "{path}"')
        button.on_click(on_button_click)
        display(button)

def set_save_directory(last_dir_file):
    """Set and remember the save directory."""
    if os.path.exists(last_dir_file):
        with open(last_dir_file, 'r') as f:
            start_dir = f.read().strip()
    else:
        start_dir = None

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    try:
        if start_dir and os.path.exists(start_dir):
            save_dir = filedialog.askdirectory(initialdir=start_dir)
        else:
            save_dir = filedialog.askdirectory()
        
        if save_dir:
            with open(last_dir_file, 'w') as f:
                f.write(save_dir)
        else:
            print("No directory selected.")
            return None
            
        return save_dir
        
    finally:
        root.quit()  # Stop the mainloop
        root.destroy()  # Ensure the Tk window is destroyed even if there's an error

