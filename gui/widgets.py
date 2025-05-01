import tkinter as tk
from tkinter import ttk


class WidgetManager:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.change_name_entry = None
        self.change_pref_entry = None
        self.change_vers_entry = None
        self.bg_color_box = None
        self.bg_color_R_scale = None
        self.bg_color_G_scale = None
        self.bg_color_B_scale = None
        self.down_text_color_box = None
        self.down_text_color_R_scale = None
        self.down_text_color_G_scale = None
        self.down_text_color_B_scale = None
        self.zero_spec_box = None
        self.zero_spec_scale = None
        self.max_spec_box = None
        self.max_spec_scale = None
        self.change_num_entry = None
        self.start_button = None
        self.progress = None
        self.label = None

    def setup_widgets(self):
        # Image and Folder Selection
        ttk.Button(self.parent, text="Select Image", command=self.parent._select_image).grid(row=0, column=0, pady=10)
        ttk.Button(self.parent, text="Choose Folder", command=self.parent._select_folder).grid(row=1, column=0, pady=10)

        # File Naming
        ttk.Label(self.parent, text="Change file's name").grid(row=3, column=0)
        self.change_name_entry = ttk.Entry(self.parent)
        self.change_name_entry.grid(row=4, column=0)

        ttk.Label(self.parent, text="Change name prefix").grid(row=5, column=0)
        self.change_pref_entry = ttk.Entry(self.parent)
        self.change_pref_entry.grid(row=6, column=0)

        ttk.Label(self.parent, text="Pic version").grid(row=7, column=0)
        self.change_vers_entry = ttk.Entry(self.parent)
        self.change_vers_entry.grid(row=8, column=0)

        ttk.Button(self.parent, text="Ok", command=self.parent._change_name).grid(row=9, column=0)

        # Background Color
        ttk.Label(self.parent, text="Top text color").grid(row=0, column=1)
        self.bg_color_box = tk.Canvas(self.parent, width=20, height=20)
        self.bg_color_box.grid(row=1, column=1)

        for i, color in enumerate(["R", "G", "B"]):
            tk.Label(self.parent, text=f"Top text color {color}:").grid(row=2 + i*2, column=1)
            scale = tk.Scale(self.parent, from_=0, to=250, length=360, orient="horizontal", command=self.parent._update_bg_color)
            scale.set(250)
            scale.grid(row=3 + i*2, column=1)
            setattr(self, f"bg_color_{color}_scale", scale)

        # Bottom Text Color
        ttk.Label(self.parent, text="Bottom text color").grid(row=0, column=2)
        self.down_text_color_box = tk.Canvas(self.parent, width=20, height=20)
        self.down_text_color_box.grid(row=1, column=2)

        for i, color in enumerate(["R", "G", "B"]):
            tk.Label(self.parent, text=f"Bottom text color {color}:").grid(row=2 + i*2, column=2)
            scale = tk.Scale(self.parent, from_=0, to=250, length=360, orient="horizontal", command=self.parent._update_down_text_color)
            scale.set(139 if color == "R" else 0)
            scale.grid(row=3 + i*2, column=2)
            setattr(self, f"down_text_color_{color}_scale", scale)

        # Hue Spectrum
        ttk.Label(self.parent, text="Min hue spectrum:").grid(row=0, column=3)
        self.zero_spec_box = tk.Canvas(self.parent, width=20, height=20)
        self.zero_spec_box.grid(row=1, column=3)
        self.zero_spec_scale = tk.Scale(self.parent, from_=0, to=360, length=360, orient="horizontal", command=self.parent._update_colors)
        self.zero_spec_scale.set(self.config.zero_spec)
        self.zero_spec_scale.grid(row=2, column=3)

        ttk.Label(self.parent, text="Max hue spectrum:").grid(row=3, column=3)
        self.max_spec_box = tk.Canvas(self.parent, width=20, height=20)
        self.max_spec_box.grid(row=4, column=3)
        self.max_spec_scale = tk.Scale(self.parent, from_=0, to=360, length=360, orient="horizontal", command=self.parent._update_colors)
        self.max_spec_scale.set(self.config.max_spec)
        self.max_spec_scale.grid(row=5, column=3)

        ttk.Label(self.parent, text="Number of changes:").grid(row=6, column=3)
        self.change_num_entry = ttk.Entry(self.parent)
        self.change_num_entry.grid(row=7, column=3)
        self.change_num_entry.insert(0, str(self.config.change_num))

        ttk.Button(self.parent, text="Apply Changes", command=self.parent._apply_values).grid(row=8, column=3, pady=10)

        # Checkboxes
        tk.Checkbutton(self.parent, text="Add Text", command=self.parent._toggle_add_text).grid(row=8, column=1)
        tk.Checkbutton(self.parent, text="Top text color black/white", command=self.parent._toggle_high_text_color).grid(row=9, column=1)

        # Save Config Button
        ttk.Button(self.parent, text="Save Config", command=self.parent._save_config).grid(row=10, column=1, pady=10)

        # Start Button and Progress
        self.start_button = ttk.Button(self.parent, text="Start Variations", command=self.parent._start_process, state=tk.DISABLED)
        self.start_button.grid(row=9, column=2, pady=10)

        self.progress = ttk.Progressbar(self.parent, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=10, column=2, pady=10)

        self.label = ttk.Label(self.parent, text="Please select an image and choose an output folder.")
        self.label.grid(row=11, column=2, pady=10)