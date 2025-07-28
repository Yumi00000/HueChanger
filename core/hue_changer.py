import numpy as np
from PIL import Image
from threading import Thread


class HueChanger(Thread):
    """
    Handles hue shifting and optional text addition for image variants.

    This class extends Thread and processes an image by creating variants with
    different hue shifts. It allows injection of dependencies such as a text adder
    for adding text overlays and a file namer for generating output file names.
    It manages the progress of its task via callbacks and supports configuration
    options for hue shifting and optional text addition. The primary goal of this
    class is to automate the generation of image variants with specified attributes.

    :ivar image_path: Path to the input image file to process.
    :type image_path: str
    :ivar output_folder: Directory path where the processed images will be saved.
    :type output_folder: str
    :ivar progress_callback: A function called with the progress index during processing.
    :type progress_callback: Callable[[int], None]
    :ivar done_callback: A function called when processing is complete.
    :type done_callback: Callable[[], None]
    :ivar config: Configuration object specifying processing parameters
                  such as hue shift bounds and slogans.
    :type config: Any
    :ivar file_namer: Object or utility used to generate output file names.
    :type file_namer: Any
    :ivar text_adder: Optional dependency to add text to images, can be injected
                      through a method call.
    :type text_adder: Any
    """
    def __init__(self, image_path, output_folder, progress_callback, done_callback, config, file_namer):
        super().__init__()
        self.image_path = image_path
        self.output_folder = output_folder
        self.progress_callback = progress_callback
        self.done_callback = done_callback
        self.config = config
        self.file_namer = file_namer
        self.text_adder = None  # To be injected if needed

    def set_text_adder(self, text_adder):
        """Inject text adder dependency."""
        self.text_adder = text_adder

    def run(self):
        original_image = Image.open(self.image_path)
        hue_shifts = np.linspace(
            self.config.zero_spec,
            self.config.max_spec,
            self.config.change_num,
            dtype=int
        )

        for idx, hue_shift in enumerate(hue_shifts):
            variant_image = self._change_hue(original_image, hue_shift)
            file_name = self.file_namer.generate_file_name(idx)
            output_path = f"{self.output_folder}/{file_name}"

            if self.text_adder and self.config.check_add_text_box:
                variant_image = self.text_adder.add_text(
                    variant_image,
                    self.config.slogans[idx % len(self.config.slogans)]
                )
            variant_image.save(output_path)
            self.progress_callback(idx)

        self.done_callback()

    @staticmethod
    def _change_hue(image, hue_shift):
        """Shift the hue of an image by a specified amount."""
        hsv_image = image.convert("HSV")
        h, s, v = hsv_image.split()
        np_h = (np.array(h) + hue_shift) % 256
        h_shifted = Image.fromarray(np_h.astype("uint8"))
        hsv_shifted_image = Image.merge("HSV", (h_shifted, s, v))
        return hsv_shifted_image.convert("RGB")