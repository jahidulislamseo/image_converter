import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import math

class UltimateImageConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Image Converter")
        self.geometry("800x700")
        self.configure(bg="#f5f5f5")
        
        # Variables
        self.input_files = []
        self.output_format = tk.StringVar(value="png")
        self.quality = tk.IntVar(value=85)
        self.resize_mode = tk.StringVar(value="percent")
        self.resize_value = tk.StringVar(value="100")
        self.width = tk.IntVar(value=0)
        self.height = tk.IntVar(value=0)
        self.target_size_kb = tk.IntVar(value=0)
        self.batch_mode = tk.BooleanVar(value=False)
        self.progress = tk.DoubleVar()
        
        self.create_ui()
        
    def create_ui(self):
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background="#f5f5f5", font=('Arial', 10))
        self.style.configure('TFrame', background="#f5f5f5")
        self.style.configure('TLabel', background="#f5f5f5")
        self.style.configure('TButton', padding=6)
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Accent.TButton', foreground='white', background='#4CAF50')
        self.style.map('Accent.TButton', background=[('active', '#45a049')])
        
        # Main container
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="ULTIMATE IMAGE CONVERTER", 
                 style="Title.TLabel").pack(pady=(0, 15))
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text=" Input Files ", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, 
                                     bg="white", bd=2, relief=tk.GROOVE,
                                     font=('Arial', 10))
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Drag and drop support
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)
        
        # Button frame
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Add Files", command=self.browse_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Add Folder", command=self.browse_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=2)
        
        # Conversion settings
        settings_frame = ttk.LabelFrame(main_frame, text=" Conversion Settings ", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Format selection
        ttk.Label(settings_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        formats = ["PNG", "JPEG", "WEBP", "GIF", "BMP", "TIFF"]
        self.format_menu = ttk.Combobox(settings_frame, textvariable=self.output_format, 
                                      values=formats, state="readonly", width=8)
        self.format_menu.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Quality settings
        ttk.Label(settings_frame, text="Quality (0-100):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(settings_frame, from_=1, to=100, variable=self.quality, 
                 orient=tk.HORIZONTAL, length=120).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        ttk.Label(settings_frame, textvariable=self.quality).grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        
        # Resize options
        resize_frame = ttk.LabelFrame(settings_frame, text=" Resize Options ", padding=10)
        resize_frame.grid(row=1, column=0, columnspan=5, sticky=tk.EW, pady=(10, 0))
        
        ttk.Radiobutton(resize_frame, text="Percentage", variable=self.resize_mode, 
                       value="percent", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        self.percent_entry = ttk.Entry(resize_frame, textvariable=self.resize_value, width=5)
        self.percent_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="%").pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(resize_frame, text="Exact Size", variable=self.resize_mode, 
                       value="exact", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="W:").pack(side=tk.LEFT, padx=2)
        self.width_entry = ttk.Entry(resize_frame, textvariable=self.width, width=5, state='disabled')
        self.width_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(resize_frame, text="H:").pack(side=tk.LEFT, padx=2)
        self.height_entry = ttk.Entry(resize_frame, textvariable=self.height, width=5, state='disabled')
        self.height_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Radiobutton(resize_frame, text="Target Size", variable=self.resize_mode, 
                       value="size", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="KB:").pack(side=tk.LEFT, padx=2)
        self.size_entry = ttk.Entry(resize_frame, textvariable=self.target_size_kb, width=5, state='disabled')
        self.size_entry.pack(side=tk.LEFT, padx=2)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Convert button
        ttk.Button(main_frame, text="START CONVERSION", command=self.start_conversion, 
                  style="Accent.TButton").pack()
        
        # Configure grid weights
        settings_frame.columnconfigure(1, weight=1)
    
    def toggle_resize_mode(self):
        state_percent = 'normal' if self.resize_mode.get() == "percent" else 'disabled'
        state_exact = 'normal' if self.resize_mode.get() == "exact" else 'disabled'
        state_size = 'normal' if self.resize_mode.get() == "size" else 'disabled'
        
        self.percent_entry.config(state=state_percent)
        self.width_entry.config(state=state_exact)
        self.height_entry.config(state=state_exact)
        self.size_entry.config(state=state_size)
        
    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        self.add_files(files)
        
    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.tiff")]
        )
        if files:
            self.add_files(files)
            
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff')):
                        files.append(os.path.join(root, filename))
            self.add_files(files)
                
    def add_files(self, files):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff')):
                if file not in self.input_files:
                    self.input_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
            else:
                messagebox.showwarning("Warning", f"Unsupported file format: {os.path.basename(file)}")
                
    def remove_files(self):
        selected = self.file_listbox.curselection()
        for index in selected[::-1]:
            self.input_files.pop(index)
            self.file_listbox.delete(index)
            
    def clear_files(self):
        self.input_files = []
        self.file_listbox.delete(0, tk.END)
        
    def start_conversion(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select at least one image file")
            return
            
        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if not output_dir:
            return
            
        thread = threading.Thread(
            target=self.convert_files,
            args=(output_dir,),
            daemon=True
        )
        thread.start()
        
    def calculate_quality(self, img, target_size_kb, output_format):
        """Calculate required quality to reach target file size"""
        min_quality = 1
        max_quality = 100
        best_quality = 85  # default
        
        for _ in range(10):  # Binary search for optimal quality
            current_quality = (min_quality + max_quality) // 2
            temp_path = os.path.join(output_dir, "temp_quality_check")
            
            save_params = {'quality': current_quality}
            if output_format == 'png':
                save_params['compress_level'] = 9 - int(current_quality / 11.11)
            
            img.save(temp_path, output_format, **save_params)
            size_kb = os.path.getsize(temp_path) / 1024
            os.remove(temp_path)
            
            if size_kb > target_size_kb:
                max_quality = current_quality - 1
            else:
                min_quality = current_quality + 1
                best_quality = current_quality
        
        return best_quality
    
    def convert_files(self, output_dir):
        total_files = len(self.input_files)
        for i, input_path in enumerate(self.input_files):
            try:
                filename = os.path.basename(input_path)
                name, ext = os.path.splitext(filename)
                output_format = self.output_format.get().lower()
                output_path = os.path.join(output_dir, f"{name}_converted.{output_format}")
                
                img = Image.open(input_path)
                
                # Apply resize based on selected mode
                if self.resize_mode.get() == "percent":
                    percent = float(self.resize_value.get())
                    if percent != 100:
                        width = int(img.width * percent / 100)
                        height = int(img.height * percent / 100)
                        img = img.resize((width, height), Image.LANCZOS)
                
                elif self.resize_mode.get() == "exact":
                    width = self.width.get()
                    height = self.height.get()
                    if width > 0 and height > 0:
                        img = img.resize((width, height), Image.LANCZOS)
                
                # Prepare save parameters
                save_params = {}
                
                if output_format in ['jpeg', 'jpg', 'webp']:
                    save_params['quality'] = self.quality.get()
                elif output_format == 'png':
                    save_params['compress_level'] = 9 - int(self.quality.get() / 11.11)
                
                # Handle target file size
                if self.resize_mode.get() == "size" and self.target_size_kb.get() > 0:
                    target_size = self.target_size_kb.get()
                    optimal_quality = self.calculate_quality(img, target_size, output_format)
                    if output_format in ['jpeg', 'jpg', 'webp']:
                        save_params['quality'] = optimal_quality
                
                # Handle transparency
                if output_format in ['jpg', 'jpeg', 'bmp'] and img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(output_path, output_format, **save_params)
                
                self.progress.set((i + 1) / total_files * 100)
                self.update_idletasks()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert {filename}:\n{str(e)}")
                
        messagebox.showinfo("Complete", "All conversions finished!")
        self.progress.set(0)

if __name__ == "__main__":
    try:
        app = UltimateImageConverter()
        app.mainloop()
    except ImportError as e:
        messagebox.showerror("Missing Dependency", f"Please install required packages:\n\npip install pillow tkinterdnd2")
