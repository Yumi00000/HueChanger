#!/usr/bin/env python
# coding: utf-8
# In[ ]:

import colorsys
import os
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import filedialog, messagebox, ttk

import easygui
import numpy as np
from PIL import Image, ImageStat, ImageDraw, ImageFont


class HueChanger(Thread):
    zero_spec = 0
    max_spec = 360
    change_num = 50
    full_progress = 100
    file_name, prefix, pic_vers = None, None, None
    font_path = 'Akrobat-Bold.otf'
    check_add_text_box = False
    bg_color = 'white'
    high_text_color_check = False
    high_text_color = 'black'
    down_text_color = '#8B0000'
    slogans = [
        ["NO ALCOHOL CHALLENGE", "ACCORDING TO THE AGE"],
        ["NO LATE EATING CHALLENGE", "ACCORDING TO THE AGE"],
        ["NO CHEAT CHALLENGE", "ACCORDING TO THE AGE"],
        ["NO SUGAR CHALLENGE", "ACCORDING TO THE AGE"],
        ["NO BAD FAT CHALLENGE", "ACCORDING TO THE AGE"]
        # Add other slogan variations here
    ]

    def __init__(self, image_path, output_folder, progress_callback, done_callback, full_name):
        super().__init__()
        self.image_path = image_path
        self.output_folder = output_folder
        self.done_callback = done_callback
        self.progress_callback = progress_callback
        self.full_name = full_name

    def run(self):
        original_image = Image.open(self.image_path)
        hue_shifts = np.linspace(self.zero_spec, self.max_spec, self.change_num, dtype=int)

        for idx, hue_shift in enumerate(hue_shifts):
            variant_image = self.change_hue(original_image, hue_shift)
            self.full_name = f'{self.file_name + "_v" + self.pic_vers + f".{idx}_" + self.prefix + ".jpg"}'
            output_path = f'{self.output_folder}/' + self.full_name

            if HueChanger.check_add_text_box:
                variant_image_with_text = self.add_text_on_top(variant_image,
                                                               self.slogans[idx % len(self.slogans)])
                variant_image_with_text.save(output_path)
            else:
                variant_image.save(output_path)
            self.progress_callback(idx)

        self.done_callback()

    @staticmethod
    def change_hue(image, hue_shift):
        # Convert image to HSV
        hsv_image = image.convert('HSV')
        h, s, v = hsv_image.split()

        # Shift hue channel
        np_h = np.array(h)
        np_h = (np_h + hue_shift) % 256
        h_shifted = Image.fromarray(np_h.astype('uint8'))

        hsv_shifted_image = Image.merge('HSV', (h_shifted, s, v))

        return hsv_shifted_image.convert('RGB')

    def add_text_on_top(self, image, slogans):

        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Using the font
        font = ImageFont.truetype(self.font_path, 100)

        # Convert the slogans list to a single string with line breaks
        text = "\n".join(slogans)

        # Determine an average color for the top 20% of the image to set as background
        top_portion = image.crop((0, 0, width, int(0.17 * height)))
        avg_color = ImageStat.Stat(top_portion).median
        # bg_color = tuple(int(c) for c in avg_color)

        # Draw a rectangle on the top 20% of the image
        draw.rectangle(((0.0, 0.0), (float(width), float(0.17 * height))), fill=self.bg_color)

        # Estimate line height and total text block height
        bbox = draw.textbbox((0, 0), "Sample", font=font)
        line_height = bbox[3] - bbox[1]
        text_block_height = line_height * len(slogans)

        # Calculate the starting y position to center the middle of the text block in the rectangle
        text_y_start = (0.14 * height / 2) - (text_block_height / 2)

        if self.high_text_color_check:
            self.high_text_color = 'white'

        # Loop through each slogan to draw them center-aligned
        for idx, line in enumerate(slogans):
            # Estimate the width of the current line
            text_width = draw.textbbox((0, 0), line, font=font)[2]
            text_x = (width - text_width) / 2  # Horizontal center alignment for each line
            #             draw.text((text_x, text_y_start + idx * line_height), line, font=font, fill="black")
            # If it's the second line, use bold font and dark-red color
            if idx == 1:
                draw.text((text_x, text_y_start + idx * line_height), line, font=font, fill=self.down_text_color)
            else:
                draw.text((text_x, text_y_start + idx * line_height), line, font=font, fill=self.high_text_color)

        return image


# This ensures non-native file dialog is used which is more compatible
tk.Tk().withdraw()


class App(tk.Tk):
    def __init__(self):
        self._var = tk.BooleanVar()
        super().__init__()

        self.iconbitmap(r"color-spectrum-1192509_1280.ico")
        self.title("Hue Changer")

        self.image_path = None
        self.folder_path = None
        self.full_name = None
        self.ok_clicked = False

        self.image_button = ttk.Button(self, text="Select Image", command=self.select_image)
        self.image_button.grid(row=0, column=0, pady=10)

        self.folder_button = ttk.Button(self, text="Choose Folder", command=self.select_folder)
        self.folder_button.grid(row=1, column=0, pady=10)

        self.change_name_label = ttk.Label(self, text="Change file's name")
        self.change_name_label.grid(row=3, column=0)
        self.change_name_entry = ttk.Entry(self)
        self.change_name_entry.grid(row=4, column=0)

        self.change_pref_label = ttk.Label(self, text="Change name prefix")
        self.change_pref_label.grid(row=5, column=0)
        self.change_pref_entry = ttk.Entry(self)
        self.change_pref_entry.grid(row=6, column=0)

        self.change_vers_label = ttk.Label(self, text="Pic version")
        self.change_vers_label.grid(row=7, column=0)
        self.change_vers_entry = ttk.Entry(self)
        self.change_vers_entry.grid(row=8, column=0)

        self.ok_button = ttk.Button(self, text="Ok", command=self.change_name)
        self.ok_button.grid(row=9, column=0)

        self.text_bg_label = ttk.Label(self, text="Top text color color")
        self.text_bg_label.grid(row=0, column=1)
        self.bg_color_box = tk.Canvas(self, width=20, height=20)
        self.bg_color_box.grid(row=1, column=1)

        self.bg_color_R_label = tk.Label(self, text="Top text color R:")
        self.bg_color_R_label.grid(row=2, column=1)
        self.bg_color_R_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                         command=self.rgb_colors_bg)
        self.bg_color_R_scale.set(250)
        self.bg_color_R_scale.grid(row=3, column=1)

        self.bg_color_G_label = tk.Label(self, text="Top text color G:")
        self.bg_color_G_label.grid(row=4, column=1)
        self.bg_color_G_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                         command=self.rgb_colors_bg)
        self.bg_color_G_scale.set(250)
        self.bg_color_G_scale.grid(row=5, column=1)

        self.bg_color_B_label = tk.Label(self, text="Top text color B:")
        self.bg_color_B_label.grid(row=6, column=1)
        self.bg_color_B_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                         command=self.rgb_colors_bg)
        self.bg_color_B_scale.set(250)
        self.bg_color_B_scale.grid(row=7, column=1)

        self.down_text_color_label = ttk.Label(self, text="Bottom text color")
        self.down_text_color_label.grid(row=0, column=2)
        self.down_text_color_box = tk.Canvas(self, width=20, height=20)
        self.down_text_color_box.grid(row=1, column=2)

        self.down_text_color_R_label = tk.Label(self, text="Bottom text color R:")
        self.down_text_color_R_label.grid(row=2, column=2)
        self.down_text_color_R_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                                command=self.rgb_down_text_colors)
        self.down_text_color_R_scale.set(139)
        self.down_text_color_R_scale.grid(row=3, column=2)

        self.down_text_color_G_label = tk.Label(self, text="Bottom text color G:")
        self.down_text_color_G_label.grid(row=4, column=2)
        self.down_text_color_G_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                                command=self.rgb_down_text_colors)
        self.down_text_color_G_scale.set(0)
        self.down_text_color_G_scale.grid(row=5, column=2)

        self.down_text_color_B_label = tk.Label(self, text="Down text color B:")
        self.down_text_color_B_label.grid(row=6, column=2)
        self.down_text_color_B_scale = tk.Scale(self, from_=0, to=250, length=360, orient="horizontal",
                                                command=self.rgb_down_text_colors)
        self.down_text_color_B_scale.set(0)
        self.down_text_color_B_scale.grid(row=7, column=2)

        self.zero_spec_label = ttk.Label(self, text="Min hues spector:")
        self.zero_spec_label.grid(row=0, column=3)
        self.zero_spec_box = tk.Canvas(self, width=20, height=20)
        self.zero_spec_box.grid(row=1, column=3)
        self.zero_spec_scale = tk.Scale(self, from_=0, to=360, length=360, orient="horizontal",
                                        command=self.update_colors)
        self.zero_spec_scale.set(HueChanger.zero_spec)
        self.zero_spec_scale.grid(row=2, column=3)

        self.max_spec_label = ttk.Label(self, text="Max hues spector:")
        self.max_spec_label.grid(row=3, column=3)
        self.max_spec_box = tk.Canvas(self, width=20, height=20)
        self.max_spec_box.grid(row=4, column=3)
        self.max_spec_scale = tk.Scale(self, from_=0, to=360, length=360, orient="horizontal",
                                       command=self.update_colors)
        self.max_spec_scale.set(HueChanger.max_spec)
        self.max_spec_scale.grid(row=5, column=3)

        self.change_num_label = ttk.Label(self, text="Numbers of changes:")
        self.change_num_label.grid(row=6, column=3)
        self.change_num_entry = ttk.Entry(self)
        self.change_num_entry.grid(row=7, column=3)

        self.apply_values = ttk.Button(self, text="Apply Changes", command=self.apply_values)
        self.apply_values.grid(row=8, column=3, pady=10)

        # self.own_slogan_label = ttk.Label(self, text="Own slogan")
        # self.own_slogan_label.pack()
        # self.own_slogan_entry = ttk.Entry(self)
        # self.own_slogan_entry.pack()

        # self.ok_slogan_button = ttk.Button(self, text="Ok", command=self.append_own_slogan)
        # self.ok_slogan_button.pack()

        self.checkbox_bg = tk.Checkbutton(self, text="Add Text", command=self.toggle_add_text)
        self.checkbox_bg.grid(row=8, column=1)

        self.checkbox_text = tk.Checkbutton(self, text="Top text color black/white", command=self.high_text_color)
        self.checkbox_text.grid(row=9, column=1)

        self.start_button = ttk.Button(self, text="Start Variations", command=self.start_process, state=tk.DISABLED)
        self.start_button.grid(row=9, column=2, pady=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=10, column=2, pady=10)

        self.label = ttk.Label(self, text="Please select an image and choose an output folder.")
        self.label.grid(row=11, column=2, pady=10)

        self.change_num_entry.insert(0, str(HueChanger.change_num))

    def select_image(self):
        self.image_path = easygui.fileopenbox(filetypes=["*.png", "*.jpg", "*.jpeg"])
        if self.folder_path and self.image_path and self.ok_clicked:
            self.start_button["state"] = tk.NORMAL

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path and self.image_path and self.ok_clicked:
            self.start_button["state"] = tk.NORMAL

    def change_name(self):
        HueChanger.file_name = str(self.change_name_entry.get())
        HueChanger.prefix = str(self.change_pref_entry.get())
        HueChanger.pic_vers = str(self.change_vers_entry.get())
        self.ok_clicked = True
        if self.folder_path and self.image_path and self.ok_clicked:
            self.start_button['state'] = tk.NORMAL

    # def append_own_slogan(self):
    #     HueChanger.slogans.append([str(self.own_slogan_entry.get())])

    def apply_values(self):
        try:
            HueChanger.zero_spec = int(self.zero_spec_scale.get())
            HueChanger.max_spec = int(self.max_spec_scale.get())
            HueChanger.change_num = int(self.change_num_entry.get())
        except ValueError:
            messagebox.showerror("Error",
                                 "Invalid input. Please enter valid num for zero_spec, max_spec, and change_num.")

    def toggle_add_text(self):
        HueChanger.check_add_text_box = not HueChanger.check_add_text_box

    def high_text_color(self):
        HueChanger.high_text_color_check = not HueChanger.high_text_color_check

    @staticmethod
    def rgb_colors(value):
        rgb_color = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(value / 360, 1, 1))
        return f"#{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}"

    def update_colors(self, value):
        hue1 = self.zero_spec_scale.get()
        hue2 = self.max_spec_scale.get()
        self.zero_spec_box.config(bg=self.rgb_colors(hue1))
        self.max_spec_box.config(bg=self.rgb_colors(hue2))

    def rgb_colors_bg(self, value):
        r = self.bg_color_R_scale.get()
        g = self.bg_color_B_scale.get()
        b = self.bg_color_G_scale.get()
        HueChanger.bg_color = f"#{r:02X}{g:02X}{b:02X}"
        self.bg_color_box.config(bg=HueChanger.bg_color)

    def rgb_down_text_colors(self, value):
        r = self.down_text_color_R_scale.get()
        g = self.down_text_color_B_scale.get()
        b = self.down_text_color_G_scale.get()
        HueChanger.down_text_color = f"#{r:02X}{g:02X}{b:02X}"
        self.down_text_color_box.config(bg=HueChanger.down_text_color)

    def start_process(self):
        if self.image_path and self.folder_path and self.ok_clicked:
            self.hue_changer = HueChanger(self.image_path, self.folder_path, self.update_progress, self.done,
                                          self.full_name)
            self.hue_changer.start()
            self.start_button["state"] = tk.DISABLED

    def update_progress(self, value):
        self.progress["value"] = value * 2

    def full_progress(self):
        if self.progress["value"] < 100:
            self.progress["value"] = HueChanger.full_progress

    def done(self):
        self.full_progress()
        self.label["text"] = "Variants created with different hues."
        self.start_button["state"] = tk.NORMAL
        folder_directory = os.path.abspath(self.folder_path)
        target_base_to_open = Path(self.hue_changer.full_name).stem + '.jpg'
        target_path_to_open = Path(folder_directory) / target_base_to_open
        os.popen(f'explorer /select,"{target_path_to_open}"')


if __name__ == '__main__':
    app = App()
    app.mainloop()
