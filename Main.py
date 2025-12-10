import re
import random
from typing import List, Tuple, Union, Dict, Any
from collections import Counter
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time

class CountingAI:
    """AI-powered counting assistant with multiple counting modes."""
    
    def __init__(self):
        self.history = []
        self.mode = "basic"
        self.custom_items = []
        self.last_result = None
    
    def basic_count(self, start: int, end: int, step: int = 1) -> List[int]:
        """Perform basic counting with specified parameters."""
        if step == 0:
            raise ValueError("Step cannot be zero")
        if start == end:
            return [start]
        if (start < end and step < 0) or (start > end and step > 0):
            return []
        
        result = list(range(start, end + (1 if step > 0 else -1), step))
        self.last_result = result
        self.history.append(("Basic Count", f"from {start} to {end} by {step}", result))
        return result
    
    def count_occurrences(self, text: str, case_sensitive: bool = False) -> Dict[str, int]:
        """Count occurrences of characters, words, or numbers in text."""
        if not case_sensitive:
            text = text.lower()
        
        # Extract words and numbers
        words = re.findall(r'\b\w+\b', text)
        # Count everything (including punctuation as individual items)
        all_chars = list(text.replace(' ', ''))  # Remove spaces for char count
        
        char_count = Counter(all_chars)
        word_count = Counter(words)
        
        result = {
            "characters": dict(char_count),
            "words": dict(word_count)
        }
        
        self.last_result = result
        self.history.append(("Count Occurrences", f"Text: '{text[:20]}...'", result))
        return result
    
    def custom_count(self, items: List[str]) -> Dict[str, int]:
        """Count occurrences in a custom list of items."""
        count = Counter(items)
        result = dict(count)
        self.last_result = result
        self.history.append(("Custom Count", f"{len(items)} items", result))
        return result
    
    def get_history(self) -> List[Tuple[str, str, Any]]:
        """Return the history of counting operations."""
        return self.history
    
    def clear_history(self):
        """Clear the operation history."""
        self.history = []
        self.last_result = None

class CountingGUI:
    """Graphical User Interface for the Counting AI."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Counting Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.ai = CountingAI()
        self.setup_ui()
        self.update_history()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Counting Assistant", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Counting Mode", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.mode_var = tk.StringVar(value="basic")
        basic_radio = ttk.Radiobutton(mode_frame, text="Basic Count", 
                                     variable=self.mode_var, value="basic",
                                     command=self.switch_mode)
        word_radio = ttk.Radiobutton(mode_frame, text="Count Occurrences", 
                                    variable=self.mode_var, value="occurrences",
                                    command=self.switch_mode)
        custom_radio = ttk.Radiobutton(mode_frame, text="Custom List Count", 
                                      variable=self.mode_var, value="custom",
                                      command=self.switch_mode)
        
        basic_radio.grid(row=0, column=0, padx=(0, 20))
        word_radio.grid(row=0, column=1, padx=(0, 20))
        custom_radio.grid(row=0, column=2)
        
        # Input area
        self.input_frame = ttk.Frame(main_frame)
        self.input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Basic mode inputs
        self.basic_frame = ttk.Frame(self.input_frame)
        self.start_label = ttk.Label(self.basic_frame, text="Start:")
        self.start_entry = ttk.Entry(self.basic_frame, width=10)
        self.start_entry.insert(0, "1")
        self.end_label = ttk.Label(self.basic_frame, text="End:")
        self.end_entry = ttk.Entry(self.basic_frame, width=10)
        self.end_entry.insert(0, "10")
        self.step_label = ttk.Label(self.basic_frame, text="Step:")
        self.step_entry = ttk.Entry(self.basic_frame, width=10)
        self.step_entry.insert(0, "1")
        
        self.start_label.grid(row=0, column=0, padx=(0, 5))
        self.start_entry.grid(row=0, column=1, padx=(0, 15))
        self.end_label.grid(row=0, column=2, padx=(0, 5))
        self.end_entry.grid(row=0, column=3, padx=(0, 15))
        self.step_label.grid(row=0, column=4, padx=(0, 5))
        self.step_entry.grid(row=0, column=5)
        
        # Occurrences mode inputs
        self.occurrences_frame = ttk.Frame(self.input_frame)
        self.text_label = ttk.Label(self.occurrences_frame, text="Text to analyze:")
        self.text_entry = ttk.Entry(self.occurrences_frame, width=50)
        self.case_var = tk.BooleanVar()
        self.case_check = ttk.Checkbutton(self.occurrences_frame, text="Case sensitive", 
                                         variable=self.case_var)
        
        self.text_label.grid(row=0, column=0, padx=(0, 10))
        self.text_entry.grid(row=0, column=1, padx=(0, 10))
        self.case_check.grid(row=0, column=2)
        
        # Custom mode inputs
        self.custom_frame = ttk.Frame(self.input_frame)
        self.custom_label = ttk.Label(self.custom_frame, text="Items (comma separated):")
        self.custom_entry = ttk.Entry(self.custom_frame, width=50)
        
        self.custom_label.grid(row=0, column=0, padx=(0, 10))
        self.custom_entry.grid(row=0, column=1)
        
        # Result display
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        main_frame.rowconfigure(3, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, width=80, height=10, 
                                                    font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.count_button = ttk.Button(button_frame, text="Count", command=self.perform_count)
        self.count_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side=tk.LEFT)
        
        # History
        history_frame = ttk.LabelFrame(main_frame, text="History", padding="10")
        history_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        main_frame.rowconfigure(5, weight=1)
        
        self.history_listbox = tk.Listbox(history_frame, width=80, height=8)
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with basic mode
        self.switch_mode()
    
    def switch_mode(self):
        """Switch between different counting modes."""
        # Hide all frames
        self.basic_frame.grid_remove()
        self.occurrences_frame.grid_remove()
        self.custom_frame.grid_remove()
        
        # Show the selected frame
        mode = self.mode_var.get()
        if mode == "basic":
            self.basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "occurrences":
            self.occurrences_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        elif mode == "custom":
            self.custom_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def perform_count(self):
        """Perform the counting operation based on the current mode."""
        mode = self.mode_var.get()
        
        try:
            if mode == "basic":
                start = int(self.start_entry.get())
                end = int(self.end_entry.get())
                step = int(self.step_entry.get())
                result = self.ai.basic_count(start, end, step)
                self.display_result("Basic Count", f"Counting from {start} to {end} by {step}:\n{result}")
                
            elif mode == "occurrences":
                text = self.text_entry.get()
                if not text:
                    messagebox.showwarning("Input Error", "Please enter text to analyze.")
                    return
                case_sensitive = self.case_var.get()
                result = self.ai.count_occurrences(text, case_sensitive)
                self.display_occurrences_result(text, result)
                
            elif mode == "custom":
                items_str = self.custom_entry.get()
                if not items_str:
                    messagebox.showwarning("Input Error", "Please enter items to count.")
                    return
                items = [item.strip() for item in items_str.split(",") if item.strip()]
                if not items:
                    messagebox.showwarning("Input Error", "Please enter valid items separated by commas.")
                    return
                result = self.ai.custom_count(items)
                self.display_custom_result(items, result)
            
            # Update history
            self.update_history()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def display_result(self, title: str, result: str):
        """Display a simple result in the result text area."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
    
    def display_occurrences_result(self, text: str, result: Dict):
        """Display the occurrences counting result."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Text analyzed: \"{text}\"\n\n")
        self.result_text.insert(tk.END, "Character counts:\n")
        for char, count in sorted(result["characters"].items()):
            self.result_text.insert(tk.END, f"  '{char}': {count}\n")
        
        self.result_text.insert(tk.END, "\nWord counts:\n")
        for word, count in sorted(result["words"].items()):
            self.result_text.insert(tk.END, f"  '{word}': {count}\n")
    
    def display_custom_result(self, items: List[str], result: Dict[str, int]):
        """Display the custom list counting result."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Items analyzed: {items}\n\n")
        self.result_text.insert(tk.END, "Count results:\n")
        for item, count in sorted(result.items()):
            self.result_text.insert(tk.END, f"  '{item}': {count}\n")
    
    def update_history(self):
        """Update the history listbox."""
        self.history_listbox.delete(0, tk.END)
        for i, (mode, description, _) in enumerate(self.ai.get_history()):
            self.history_listbox.insert(tk.END, f"{i+1}. {mode} - {description}")
    
    def clear_history(self):
        """Clear the operation history."""
        self.ai.clear_history()
        self.update_history()
        self.result_text.delete(1.0, tk.END)

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = CountingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
