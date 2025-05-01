import tkinter as tk
from tkinter import filedialog, messagebox
import easygui
import os
from pathlib import Path
import colorsys
from config.settings import ConfigError
from .widgets import WidgetManager
from core.hue_changer import HueChanger
from core.text_adder import TextAdder
from core.file_namer import FileNamer
from config.settings import ConfigFactory


class App(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.file_namer = FileNamer()
        self.image_path = None
        self.folder_path = None
        self.ok_clicked = False
        self.hue_changer = None  # Track the HueChanger thread
        self._setup_window()
        self.widget_manager = WidgetManager(self, config)
        self.widget_manager.setup_widgets()
        # Bind the close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_window(self):
        self.title("Hue Changer")

    def _select_image(self):
        self.image_path = easygui.fileopenbox(filetypes=["*.png", "*.jpg", "*.jpeg"])
        self._update_start_button_state()

    def _select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self._update_start_button_state()

    def _change_name(self):
        self.file_namer.set_name(
            self.widget_manager.change_name_entry.get(),
            self.widget_manager.change_pref_entry.get(),
            self.widget_manager.change_vers_entry.get()
        )
        self.ok_clicked = True
        self._update_start_button_state()

    def _apply_values(self):
        try:
            self.config.zero_spec = int(self.widget_manager.zero_spec_scale.get())
            self.config.max_spec = int(self.widget_manager.max_spec_scale.get())
            self.config.change_num = int(self.widget_manager.change_num_entry.get())
            self.config.validate()
        except (ValueError, ConfigError) as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def _toggle_add_text(self):
        self.config.check_add_text_box = not self.config.check_add_text_box

    def _toggle_high_text_color(self):
        self.config.high_text_color_check = not self.config.high_text_color_check

    def _update_bg_color(self, value):
        r = self.widget_manager.bg_color_R_scale.get()
        g = self.widget_manager.bg_color_G_scale.get()
        b = self.widget_manager.bg_color_B_scale.get()
        self.config.bg_color = f"#{r:02X}{g:02X}{b:02X}"
        self.widget_manager.bg_color_box.config(bg=self.config.bg_color)

    def _update_down_text_color(self, value):
        r = self.widget_manager.down_text_color_R_scale.get()
        g = self.widget_manager.down_text_color_G_scale.get()
        b = self.widget_manager.down_text_color_B_scale.get()
        self.config.down_text_color = f"#{r:02X}{g:02X}{b:02X}"
        self.widget_manager.down_text_color_box.config(bg=self.config.down_text_color)

    def _update_colors(self, value):
        hue1 = self.widget_manager.zero_spec_scale.get()
        hue2 = self.widget_manager.max_spec_scale.get()
        self.widget_manager.zero_spec_box.config(bg=self._rgb_colors(hue1))
        self.widget_manager.max_spec_box.config(bg=self._rgb_colors(hue2))

    @staticmethod
    def _rgb_colors(value):
        rgb_color = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(value / 360, 1, 1))
        return f"#{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"

    def _update_start_button_state(self):
        if self.image_path and self.folder_path and self.ok_clicked:
            self.widget_manager.start_button["state"] = tk.NORMAL
        else:
            self.widget_manager.start_button["state"] = tk.DISABLED

    def _save_config(self):
        try:
            ConfigFactory.save_config(self.config)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except ConfigError as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def _start_process(self):
        if self.image_path and self.folder_path and self.ok_clicked:
            self.hue_changer = HueChanger(
                self.image_path,
                self.folder_path,
                self._update_progress,
                self._done,
                self.config,
                self.file_namer
            )
            self.hue_changer.set_text_adder(TextAdder(self.config))
            self.hue_changer.start()
            self.widget_manager.start_button["state"] = tk.DISABLED

    def _update_progress(self, value):
        self.widget_manager.progress["value"] = value * 2

    def _done(self):
        self.widget_manager.progress["value"] = self.config.full_progress
        self.widget_manager.label["text"] = "Variants created with different hues."
        self.widget_manager.start_button["state"] = tk.NORMAL
        folder_directory = os.path.abspath(self.folder_path)
        target_base_to_open = Path(self.file_namer.generate_file_name(0)).stem + ".jpg"
        target_path_to_open = Path(folder_directory) / target_base_to_open
        os.popen(f'explorer /select,"{target_path_to_open}"')

    def _on_closing(self):
        """Handle window close event."""
        # Stop the HueChanger thread if it's running
        if self.hue_changer and self.hue_changer.is_alive():
            self.hue_changer.stop()
            self.hue_changer.join()  # Wait for the thread to finish
        # Destroy the Tkinter window
        self.destroy()