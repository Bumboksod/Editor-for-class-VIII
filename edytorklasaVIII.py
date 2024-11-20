import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import threading
import os


class PythonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Editor")
        self.text_area = tk.Text(root, wrap='none', undo=True, font=("Courier New", 12))
        self.text_area.pack(fill=tk.BOTH, expand=1)
        
        # Scrollbars
        self.scroll_x = tk.Scrollbar(self.text_area, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = tk.Scrollbar(self.text_area, orient=tk.VERTICAL, command=self.text_area.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        # Menu
        self.create_menu()
        
        # Bind key events
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_code)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        
        self.root.config(menu=menu_bar)
    
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
    
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
    
    def run_code(self):
        code = self.text_area.get(1.0, tk.END)
        temp_file = "temp_turtle_script.py"
        
        # Zapisz kod do tymczasowego pliku
        with open(temp_file, "w") as file:
            file.write(code)
        
        # Uruchom kod w osobnym wątku, aby nie blokować GUI
        threading.Thread(target=self.execute_code, args=(temp_file,), daemon=True).start()
    
    def execute_code(self, script_path):
        try:
            # Ukryj konsolę systemową
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Uruchom skrypt w nowym procesie
            result = subprocess.run(
                ["python", script_path],
                startupinfo=startupinfo,
                capture_output=True,
                text=True
            )
            
            # Usuń plik tymczasowy po wykonaniu
            os.remove(script_path)
            
            # Wyświetl wynik w oknie dialogowym
            self.display_output(result.stdout, result.stderr)
        
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_output(self, stdout, stderr):
        # Nowe okno jako konsola
        console_window = tk.Toplevel(self.root)
        console_window.title("Output Console")
        console_text = tk.Text(console_window, wrap='word', font=("Courier New", 12))
        console_text.pack(fill=tk.BOTH, expand=1)
        
        if stdout:
            console_text.insert(tk.END, stdout)
        if stderr:
            console_text.insert(tk.END, "\n" + stderr)
        
        console_text.configure(state="disabled")
    
    def highlight_syntax(self, event=None):
        keywords = {"def", "return", "if", "else", "elif", "import", "for", "while", "class", "try", "except", "finally", "with", "as"}
        text = self.text_area.get(1.0, tk.END)
        
        # Reset text styling
        self.text_area.tag_remove("keyword", "1.0", tk.END)
        
        for word in keywords:
            start_idx = "1.0"
            while True:
                start_idx = self.text_area.search(rf"\b{word}\b", start_idx, stopindex=tk.END, regexp=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(word)}c"
                self.text_area.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx
        
        self.text_area.tag_config("keyword", foreground="blue", font=("Courier New", 12, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    editor = PythonEditor(root)
    root.mainloop()
