from PIL import ImageDraw, ImageFont, ImageStat
import logging

logger = logging.getLogger(__name__)

class TextAdder:
    def __init__(self, config):
        self.config = config
        self.font = self._load_font()

    def _load_font(self):
        """Load font, falling back to PIL's default if necessary."""
        font_size = 50  # Reduced font size for better fit
        try:
            logger.debug(f"Attempting to load font: {self.config.font_path}")
            return ImageFont.truetype(self.config.font_path, font_size)
        except (IOError, OSError) as e:
            logger.warning(f"Failed to load font {self.config.font_path}: {str(e)}. Falling back to default.")
            try:
                default_font = self.config.DEFAULT_FONT_PATH
                logger.debug(f"Attempting to load default font: {default_font}")
                return ImageFont.truetype(default_font, font_size)
            except (IOError, OSError) as e:
                logger.warning(f"Default font {default_font} not found: {str(e)}. Using PIL default font.")
                # Use PIL's default font as a last resort
                return ImageFont.load_default()

    def _validate_colors(self):
        """Ensure text colors are visible against the background."""
        bg_color = self.config.bg_color.lower()
        high_text_color = "white" if self.config.high_text_color_check else self.config.high_text_color.lower()
        down_text_color = self.config.down_text_color.lower()

        # Ensure colors are in hex format or valid color names
        for color, name in [(bg_color, "background"), (high_text_color, "high text"), (down_text_color, "down text")]:
            if not (color.startswith("#") or color in {"white", "black", "red", "blue", "green"}):  # Add more as needed
                logger.warning(f"Invalid {name} color '{color}'. Defaulting to black.")
                if name == "background":
                    bg_color = "white"
                elif name == "high text":
                    high_text_color = "black"
                else:
                    down_text_color = "#8B0000"

        # Warn if text color matches background
        if bg_color == high_text_color:
            logger.warning(f"High text color {high_text_color} matches background {bg_color}. Changing to black.")
            high_text_color = "black"
        if bg_color == down_text_color:
            logger.warning(f"Down text color {down_text_color} matches background {bg_color}. Changing to dark red.")
            down_text_color = "#8B0000"

        return bg_color, high_text_color, down_text_color

    def add_text(self, image, slogans):
        """Add text slogans to the top portion of the image."""
        if self.font is None:
            logger.warning("No valid font available. Skipping text rendering.")
            return image

        if not slogans or not all(isinstance(line, str) for line in slogans):
            logger.warning(f"Invalid slogans: {slogans}. Skipping text rendering.")
            return image

        # Ensure image is in RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")

        draw = ImageDraw.Draw(image)
        width, height = image.size
        logger.debug(f"Image size: {width}x{height}")

        # Draw background rectangle (15% of image height)
        rect_height = int(0.15 * height)
        bg_color, high_text_color, down_text_color = self._validate_colors()
        draw.rectangle(
            ((0.0, 0.0), (float(width), float(rect_height))),
            fill=bg_color
        )

        # Calculate text positioning
        text_lines = slogans
        bbox = draw.textbbox((0, 0), "Sample", font=self.font)
        line_height = bbox[3] - bbox[1]
        text_block_height = line_height * len(text_lines)
        # Center text vertically in the rectangle
        text_y_start = (rect_height - text_block_height) / 2
        logger.debug(f"Text block height: {text_block_height}, Text y start: {text_y_start}")

        # Draw each slogan
        for idx, line in enumerate(text_lines):
            # Ensure line is a string and strip any whitespace
            line = str(line).strip()
            if not line:
                continue
            text_width = draw.textbbox((0, 0), line, font=self.font)[2]
            text_x = (width - text_width) / 2  # Center horizontally
            text_y = text_y_start + idx * line_height
            logger.debug(f"Line {idx}: '{line}', x: {text_x}, y: {text_y}")
            text_color = down_text_color if idx == 1 else high_text_color
            draw.text(
                (text_x, text_y),
                line,
                font=self.font,
                fill=text_color
            )

        return image