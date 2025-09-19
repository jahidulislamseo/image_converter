import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageOps
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading

FORMAT_MAP = {
    "PNG": "PNG",
    "JPEG": "JPEG",
    "WEBP": "WEBP",
    "GIF": "GIF",
    "BMP": "BMP",
    "TIFF": "TIFF",
}

EXT_MAP = {
    "PNG": "png",
    "JPEG": "jpg",
    "WEBP": "webp",
    "GIF": "gif",
    "BMP": "bmp",
    "TIFF": "tiff",
}

class UltimateImageConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Image Converter")
        self.geometry("800x700")
        self.configure(bg="#f5f5f5")

        # Variables
        self.input_files = []
        self.output_format = tk.StringVar(value="PNG")  # match combobox values
        self.quality = tk.IntVar(value=85)
        self.resize_mode = tk.StringVar(value="percent")
        self.resize_value = tk.StringVar(value="100")
        self.width = tk.IntVar(value=0)
        self.height = tk.IntVar(value=0)
        self.target_size_kb = tk.IntVar(value=0)
        self.progress = tk.DoubleVar(value=0.0)

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
        ttk.Label(main_frame, text="ULTIMATE IMAGE CONVERTER", style="Title.TLabel").pack(pady=(0, 15))

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text=" Input Files ", padding=10)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED, bg="white", bd=2, relief=tk.GROOVE, font=('Arial', 10))
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
        formats = list(FORMAT_MAP.keys())
        self.format_menu = ttk.Combobox(settings_frame, textvariable=self.output_format, values=formats, state="readonly", width=8)
        self.format_menu.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        # Quality settings
        ttk.Label(settings_frame, text="Quality (1-100):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(settings_frame, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL, length=120)\
            .grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        ttk.Label(settings_frame, textvariable=self.quality).grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)

        # Resize options
        resize_frame = ttk.LabelFrame(settings_frame, text=" Resize Options ", padding=10)
        resize_frame.grid(row=1, column=0, columnspan=5, sticky=tk.EW, pady=(10, 0))

        ttk.Radiobutton(resize_frame, text="Percentage", variable=self.resize_mode, value="percent", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        self.percent_entry = ttk.Entry(resize_frame, textvariable=self.resize_value, width=5)
        self.percent_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="%").pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(resize_frame, text="Exact Size", variable=self.resize_mode, value="exact", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="W:").pack(side=tk.LEFT, padx=2)
        self.width_entry = ttk.Entry(resize_frame, textvariable=self.width, width=5, state='disabled')
        self.width_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(resize_frame, text="H:").pack(side=tk.LEFT, padx=2)
        self.height_entry = ttk.Entry(resize_frame, textvariable=self.height, width=5, state='disabled')
        self.height_entry.pack(side=tk.LEFT, padx=2)

        ttk.Radiobutton(resize_frame, text="Target Size", variable=self.resize_mode, value="size", command=self.toggle_resize_mode).pack(side=tk.LEFT, padx=5)
        ttk.Label(resize_frame, text="KB:").pack(side=tk.LEFT, padx=2)
        self.size_entry = ttk.Entry(resize_frame, textvariable=self.target_size_kb, width=6, state='disabled')
        self.size_entry.pack(side=tk.LEFT, padx=2)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))

        # Convert button
        ttk.Button(main_frame, text="START CONVERSION", command=self.start_conversion, style="Accent.TButton").pack()

        settings_frame.columnconfigure(1, weight=1)

    def toggle_resize_mode(self):
        mode = self.resize_mode.get()
        self.percent_entry.config(state='normal' if mode == "percent" else 'disabled')
        self.width_entry.config(state='normal' if mode == "exact" else 'disabled')
        self.height_entry.config(state='normal' if mode == "exact" else 'disabled')
        self.size_entry.config(state='normal' if mode == "size" else 'disabled')

    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        self.add_files(files)

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.tiff *.tif")]
        )
        if files:
            self.add_files(files)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff', '.tif')):
                        files.append(os.path.join(root, filename))
            self.add_files(files)

    def add_files(self, files):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff', '.tif')):
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

        t = threading.Thread(target=self.convert_files_worker, args=(output_dir,), daemon=True)
        t.start()

    # --- Worker & helpers (no UI calls directly) ---

    def _calc_quality_for_target(self, img, target_kb, fmt, base_params):
        """
        Binary search JPEG/WEBP quality to get close to target_kb.
        Uses in-memory buffer. Returns best quality found.
        """
        if fmt not in ("JPEG", "WEBP"):
            return None  # Only meaningful for these formats

        lo, hi = 1, 100
        best_q = self.quality.get()
        for _ in range(10):
            q = (lo + hi) // 2
            params = dict(base_params)
            params["quality"] = q
            buf = io.BytesIO()
            img.save(buf, fmt, **params)
            size_kb = len(buf.getvalue()) / 1024.0
            if size_kb > target_kb:
                hi = q - 1
            else:
                best_q = q
                lo = q + 1
        return best_q

    def _build_save_params(self, fmt):
        """
        Return default save params per format for given UI quality.
        """
        q = max(1, min(int(self.quality.get()), 100))
        if fmt in ("JPEG", "WEBP"):
            return {"quality": q}
        elif fmt == "PNG":
            # Map quality (1-100) to compress_level (9..0), clamp 0..9
            comp = 9 - int(q / 11.12)
            comp = max(0, min(comp, 9))
            return {"optimize": True, "compress_level": comp}
        else:
            return {}

    def convert_files_worker(self, output_dir):
        total = len(self.input_files)

        for i, input_path in enumerate(self.input_files):
            filename = os.path.basename(input_path)
            name, _ = os.path.splitext(filename)
            try:
                fmt = FORMAT_MAP[self.output_format.get()]
                ext = EXT_MAP[fmt]

                # Avoid overwriting existing files
                output_path = os.path.join(output_dir, f"{name}_converted.{ext}")
                counter = 1
                while os.path.exists(output_path):
                    output_path = os.path.join(output_dir, f"{name}_converted_{counter}.{ext}")
                    counter += 1

                with Image.open(input_path) as img_raw:
                    img = ImageOps.exif_transpose(img_raw)

                    # Resize
                    if self.resize_mode.get() == "percent":
                        percent = float(self.resize_value.get() or "100")
                        if percent != 100:
                            new_w = max(1, int(img.width * percent / 100))
                            new_h = max(1, int(img.height * percent / 100))
                            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                    elif self.resize_mode.get() == "exact":
                        w = int(self.width.get() or 0)
                        h = int(self.height.get() or 0)
                        if w > 0 and h > 0:
                            img = img.resize((w, h), Image.Resampling.LANCZOS)

                    # Transparency handling for formats that don't support alpha
                    if fmt in ("JPEG", "BMP", "TIFF") and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    save_params = self._build_save_params(fmt)

                    # Target size handling (JPEG/WEBP only makes sense)
                    if self.resize_mode.get() == "size" and self.target_size_kb.get() > 0:
                        best_q = self._calc_quality_for_target(img, self.target_size_kb.get(), fmt, save_params)
                        if best_q is not None:
                            save_params["quality"] = best_q

                    # Save
                    img.save(output_path, fmt, **save_params)

                # progress update on main thread
                self.after(0, lambda done=i + 1: self.progress.set(done / total * 100))

            except Exception as e:
                # show error on main thread
                self.after(0, lambda fn=filename, err=str(e): messagebox.showerror("Error", f"Failed to convert {fn}:\n{err}"))

        # reset + done dialog on main thread
        def _done():
            messagebox.showinfo("Complete", "All conversions finished!")
            self.progress.set(0)
        self.after(0, _done)

if __name__ == "__main__":
    try:
        app = UltimateImageConverter()
        app.mainloop()
    except ImportError:
        # Avoid calling messagebox if Tk couldn't init; print instead.
        print("Missing Dependency:\n\npip install pillow tkinterdnd2")
