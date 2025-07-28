from PIL import Image, ImageEnhance, ImageOps
import colorsys
import numpy as np

class ImageEditor:
    """
    Handles loading, editing, and displaying images, including applying hue shifts.

    This class provides functionality to load an image, display a resized version,
    and apply a hue shift effect to modify its color. The hue shifting operates
    incrementally, allowing iterative adjustments to the image. The original loaded
    image is maintained separately to reset edits as needed.

    :ivar image: The current state of the image being edited.
    :type image: Image.Image or None
    :ivar original_image: The unedited, original image loaded by the editor.
    :type original_image: Image.Image or None
    :ivar hue_shift: The current incremental hue shift factor applied to the image.
    :type hue_shift: float
    """
    def __init__(self):
        self.image = None
        self.original_image = None
        self.hue_shift = 0

    def load_image(self, path):
        self.original_image = Image.open(path).convert("RGB")
        self.image = self.original_image.copy()

    def get_display_image(self):
        return self.image.resize((500, 400), Image.LANCZOS)

    def shift_hue(self):
        if not self.image:
            return

        img = self.original_image.copy()
        arr = np.array(img).astype('float32') / 255.0
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        h, s, v = np.vectorize(colorsys.rgb_to_hsv)(r, g, b)
        h = (h + self.hue_shift) % 1.0
        r, g, b = np.vectorize(colorsys.hsv_to_rgb)(h, s, v)
        arr = np.stack([r, g, b], axis=-1) * 255
        arr = arr.astype('uint8')
        self.image = Image.fromarray(arr)
        self.hue_shift = (self.hue_shift + 0.01) % 1.0  # Ensure hue_shift stays within bounds


def change_hue(image: Image.Image, hue: float) -> Image.Image:
    """
    Changes the hue of the given image to the specified value. The hue of all
    pixels in the image is modified, while the saturation and value (brightness)
    remain unchanged. The image is processed in the RGB color space and converted
    temporarily to HSV color space for adjusting the hue.

    :param image: The input image whose hue is to be modified.
    :type image: Image.Image
    :param hue: The desired hue value to set for the image. The value should
        be in degrees ranging from 0 to 360.
    :type hue: float
    :return: A new image object with the adjusted hue, maintaining the
        original saturation and brightness levels.
    :rtype: Image.Image
    """
    img = image.convert('RGB')
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            h = hue / 360.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            pixels[x, y] = int(r*255), int(g*255), int(b*255)

    return img

