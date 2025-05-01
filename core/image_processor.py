from PIL import Image, ImageEnhance, ImageOps
import colorsys
import numpy as np

class ImageEditor:
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

