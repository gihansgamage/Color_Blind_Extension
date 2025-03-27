import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from ttkbootstrap import Style
import cv2
import numpy as np
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

class EnhancedColorAidApp:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme='morph')
        self.root.title("ColorAid Pro")
        self.root.geometry("1200x800")
        
        # Settings
        self.settings = {
            'contrast': 1.3,
            'hue': 20,
            'darkMode': False,
            'blueLight': False,
            'readingMode': False
        }
        
        # Media Handling
        self.original_content = None
        self.processed_content = None
        self.current_media_type = None
        self.video_capture = None
        self.video_running = False
        
        # GUI Components
        self.create_widgets()
        self.create_menu()
        self.create_status_bar()
        
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Image", command=lambda: self.load_media('image'))
        file_menu.add_command(label="Open Video", command=lambda: self.load_media('video'))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)
    
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_widgets(self):
        # Control Panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input Fields
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(side=tk.LEFT, padx=10)
        
        # Contrast Controls
        ttk.Label(input_frame, text="Contrast:").grid(row=0, column=0)
        self.contrast_slider = ttk.Scale(input_frame, from_=1, to=2, value=1.3, 
                                       command=lambda e: self.apply_filters())
        self.contrast_slider.grid(row=0, column=1, padx=5)
        self.contrast_entry = ttk.Entry(input_frame, width=5)
        self.contrast_entry.insert(0, "1.3")
        self.contrast_entry.grid(row=0, column=2, padx=5)
        ttk.Button(input_frame, text="↺", width=2, 
                 command=self.reset_contrast).grid(row=0, column=3, padx=5)
        
        # Hue Controls
        ttk.Label(input_frame, text="Hue:").grid(row=1, column=0)
        self.hue_slider = ttk.Scale(input_frame, from_=0, to=360, value=20, 
                                 command=lambda e: self.apply_filters())
        self.hue_slider.grid(row=1, column=1, padx=5)
        self.hue_entry = ttk.Entry(input_frame, width=5)
        self.hue_entry.insert(0, "20")
        self.hue_entry.grid(row=1, column=2, padx=5)
        ttk.Button(input_frame, text="↺", width=2, 
                 command=self.reset_hue).grid(row=1, column=3, padx=5)
        
        # Checkboxes
        check_frame = ttk.Frame(control_frame)
        check_frame.pack(side=tk.LEFT, padx=20)
        
        self.dark_mode = tk.BooleanVar()
        ttk.Checkbutton(check_frame, text="Invert", variable=self.dark_mode, 
                      command=self.apply_filters).pack(anchor=tk.W)
        
        self.blue_light = tk.BooleanVar()
        ttk.Checkbutton(check_frame, text="Blue Light", variable=self.blue_light,
                      command=self.apply_filters).pack(anchor=tk.W)
        
        self.reading_mode = tk.BooleanVar()
        ttk.Checkbutton(check_frame, text="Reading Mode", variable=self.reading_mode,
                      command=self.apply_filters).pack(anchor=tk.W)
        
        # Preset Filters
        preset_frame = ttk.Frame(control_frame)
        preset_frame.pack(side=tk.RIGHT, padx=10)
        
        self.preset_var = tk.StringVar()
        presets = ttk.Combobox(preset_frame, textvariable=self.preset_var, 
                             values=[
                                 "Default", 
                                 "Protanopia (Red-blind)", 
                                 "Deuteranopia (Green-blind)", 
                                 "Tritanopia (Blue-blind)", 
                                 "Reading Mode"
                             ], state="readonly", width=25)
        presets.bind("<<ComboboxSelected>>", self.apply_preset)
        presets.pack(side=tk.LEFT, padx=5)
        presets.current(0)
        
        # URL Input
        ttk.Button(preset_frame, text="Load URL", command=self.load_url).pack(side=tk.LEFT, padx=5)
        
        # Display Area
        display_frame = ttk.Frame(self.root)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.original_panel = ttk.LabelFrame(display_frame, text="Original")
        self.original_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_label = ttk.Label(self.original_panel)
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        self.processed_panel = ttk.LabelFrame(display_frame, text="Processed")
        self.processed_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.processed_label = ttk.Label(self.processed_panel)
        self.processed_label.pack(fill=tk.BOTH, expand=True)
    
    def reset_contrast(self):
        self.contrast_slider.set(1.3)
        self.contrast_entry.delete(0, tk.END)
        self.contrast_entry.insert(0, "1.3")
        self.apply_filters()
    
    def reset_hue(self):
        self.hue_slider.set(20)
        self.hue_entry.delete(0, tk.END)
        self.hue_entry.insert(0, "20")
        self.apply_filters()
    
    def load_media(self, media_type):
        if media_type == 'image':
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
            if path:
                self.current_media_type = 'image'
                self.original_content = cv2.imread(path)
                self.show_original_content()
                self.apply_filters()
        
        elif media_type == 'video':
            path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
            if path:
                self.current_media_type = 'video'
                self.video_capture = cv2.VideoCapture(path)
                self.play_video()
    
    def load_url(self):
        url = simpledialog.askstring("Load Image from URL", "Enter image URL:")
        if url:
            try:
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                self.original_content = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                self.current_media_type = 'image'
                self.show_original_content()
                self.apply_filters()
                self.status_bar.config(text=f"Loaded image from: {url}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def play_video(self):
        if self.video_capture.isOpened():
            self.video_running = True
            threading.Thread(target=self.process_video, daemon=True).start()
    
    def process_video(self):
        while self.video_running:
            ret, frame = self.video_capture.read()
            if ret:
                processed_frame = self.apply_filters_to_frame(frame)
                self.display_frame(processed_frame)
            else:
                self.video_running = False
            self.root.update()
    
    def apply_filters_to_frame(self, frame):
        # Apply current filters to video frame
        frame = cv2.convertScaleAbs(frame, alpha=float(self.contrast_slider.get()), beta=0)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[..., 0] = (hsv[..., 0] + int(self.hue_slider.get())//2) % 180
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        if self.dark_mode.get():
            frame = cv2.bitwise_not(frame)
        
        if self.blue_light.get():
            frame = self.apply_sepia(frame)
        
        if self.reading_mode.get():
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        return frame
    
    def display_frame(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((800, 600))
        img_tk = ImageTk.PhotoImage(img)
        self.processed_label.config(image=img_tk)
        self.processed_label.image = img_tk
    
    def show_original_content(self):
        if self.current_media_type == 'image':
            img = cv2.cvtColor(self.original_content, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img.thumbnail((800, 600))
            img_tk = ImageTk.PhotoImage(img)
            self.original_label.config(image=img_tk)
            self.original_label.image = img_tk
    
    def apply_filters(self, *args):
        if self.current_media_type == 'image' and self.original_content is not None:
            processed = self.original_content.copy()
            processed = cv2.convertScaleAbs(processed, alpha=float(self.contrast_slider.get()), beta=0)
            
            hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
            hsv[..., 0] = (hsv[..., 0] + int(self.hue_slider.get())//2) % 180
            processed = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            if self.dark_mode.get():
                processed = cv2.bitwise_not(processed)
            
            if self.blue_light.get():
                processed = self.apply_sepia(processed)
            
            if self.reading_mode.get():
                processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
                processed = cv2.convertScaleAbs(processed, alpha=1.5, beta=0)
            
            self.show_processed_image(processed)
    
    def apply_sepia(self, img):
        kernel = np.array([[0.272, 0.534, 0.131],
                         [0.349, 0.686, 0.168],
                         [0.393, 0.769, 0.189]])
        return cv2.transform(img, kernel).clip(0, 255).astype(np.uint8)
    
    def show_processed_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((800, 600))
        img_tk = ImageTk.PhotoImage(img)
        self.processed_label.config(image=img_tk)
        self.processed_label.image = img_tk
    
    def apply_preset(self, event):
        preset = self.preset_var.get()
        descriptions = {
            "Protanopia (Red-blind)": "Red color deficiency - enhances contrast for red-blindness",
            "Deuteranopia (Green-blind)": "Green color deficiency - enhances green perception",
            "Tritanopia (Blue-blind)": "Blue color deficiency - enhances blue perception",
            "Reading Mode": "High contrast grayscale for better text readability"
        }
        
        self.status_bar.config(text=descriptions.get(preset, "Default settings restored"))
        
        if "Protanopia" in preset:
            self.contrast_slider.set(1.5)
            self.hue_slider.set(180)
        elif "Deuteranopia" in preset:
            self.contrast_slider.set(1.4)
            self.hue_slider.set(90)
        elif "Tritanopia" in preset:
            self.contrast_slider.set(1.6)
            self.hue_slider.set(270)
        elif "Reading" in preset:
            self.contrast_slider.set(1.8)
            self.hue_slider.set(0)
            self.reading_mode.set(True)
        else:
            self.contrast_slider.set(1.3)
            self.hue_slider.set(20)
            self.reading_mode.set(False)
        
        self.dark_mode.set(False)
        self.blue_light.set(False)
        self.apply_filters()
    
    def on_closing(self):
        self.video_running = False
        if self.video_capture:
            self.video_capture.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedColorAidApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()