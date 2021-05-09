"""
Screen
"""
import asyncio
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5


class Screen:
    def __init__(self):
        # Define the Reset Pin
        self.oled_reset = digitalio.DigitalInOut(board.D4)
        # Use for I2C.
        self.i2c = board.I2C()
        self.oled = adafruit_ssd1306.SSD1306_I2C(WIDTH,
                                                 HEIGHT,
                                                 self.i2c,
                                                 addr=0x3D,
                                                 reset=self.oled_reset)
        # Load default font.
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSans-BoldItalic.ttf", 12)

        self.gif_run = None

    def stop(self):
        pass

    def clear(self):
        # Clear display.
        self.oled.fill(0)
        self.oled.show()

    def create_blank_image(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        image = Image.new("1", (self.oled.width, self.oled.height))
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        return image, draw

    def draw_text_box(self, text):
        self.clear()
        image, draw = self.create_blank_image()

        # Draw a white background
        draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)

        # Draw a smaller inner rectangle
        draw.rectangle(
            (BORDER, BORDER, self.oled.width - BORDER - 1, self.oled.height - BORDER - 1),
            outline=0,
            fill=0,
        )

        # Draw Some Text
        (font_width, font_height) = self.font.getsize(text)
        draw.text(
            (self.oled.width // 2 - font_width // 2, self.oled.height // 2 - font_height // 2),
            text,
            font=self.font,
            fill=255,
        )

        # Display image
        self.oled.image(image)
        self.oled.show()

    def draw_text(self, text):
        self.clear()
        image, draw = self.create_blank_image()

        # Draw Some Text
        (font_width, font_height) = self.font.getsize(text)
        draw.text(
            (self.oled.width // 2 - font_width // 2, self.oled.height // 2 - font_height // 2),
            text,
            font=self.font,
            fill=255,
        )

        # Display image
        self.oled.image(image)
        self.oled.show()

    def draw_menu(self, previous, current, next):
        self.clear()
        image, draw = self.create_blank_image()

        (font_width, font_height) = self.font.getsize(current)

        # Draw Some Text
        draw.text(
            (3, 5),
            f"{previous}\n->   {current}\n{next}",
            font=self.font,
            fill=0,
        )

        # Display image
        self.oled.image(image)
        self.oled.show()

    def get_loading(self):
        images = []

        center = self.oled.width // 2
        color_1 = 0
        color_2 = 255
        max_radius = int(center)
        step = 8

        for i in range(0, max_radius, step):
            image, draw = self.create_blank_image()
            draw.ellipse((center - i, center - i, center + i, center + i), fill=color_2)
            images.append(image)

        for i in range(0, max_radius, step):
            image, draw = self.create_blank_image()
            draw.ellipse((center - i, center - i, center + i, center + i), fill=color_1)
            images.append(image)

        return images

    async def draw_image(self, image, clear=False):
        if clear:
            self.clear()
        self.oled.image(image)
        self.oled.show()

    def stop_gif(self):
        self.gif_run = True

    async def start_gif(self, gif_images):
        self.gif_run = True
        while self.gif_run:
            for image in gif_images:
                await self.draw_image(image)
                await asyncio.sleep(0.1)
