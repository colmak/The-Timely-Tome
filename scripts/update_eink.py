#!/usr/bin/env python3
import os
os.environ["DISPLAY"] = ":0"
import random
import datetime
from PIL import Image, ImageDraw, ImageFont
import logging
import time

# Configure logging to output to a file (this file will be appended)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filename='/home/admin/eink_debug.log',
    filemode='a'
)

# If you also want messages to appear on the console (optional)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Import Waveshare e-Paper driver
import sys
sys.path.append('/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib')  
sys.path.append('/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd')  # Correct path to Waveshare drivers

import epd4in26  # Import the correct e-Paper display driver

# Set correct dimensions for 4.26-inch e-Paper display
EPD_WIDTH = 800  
EPD_HEIGHT = 480
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")

UPDATE_COUNT = 10  # Only do full clears every 10 updates
counter_file = "/home/admin/The-Timely-Tome/scripts/update_counter.txt"

def get_update_count():
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            return int(f.read().strip())
    return 0

def save_update_count(count):
    with open(counter_file, "w") as f:
        f.write(str(count))

def pick_random_image_for_current_minute():
    now = datetime.datetime.now()
    time_str = now.strftime("%H-%M")
    matching = [fname for fname in os.listdir(IMAGES_DIR) if fname.startswith(time_str) and fname.endswith(".png")]
    
    if not matching:
        # Fallback to any available image if no exact match found
        all_pngs = [f for f in os.listdir(IMAGES_DIR) if f.endswith(".png")]
        if not all_pngs:
            logging.warning("No PNG images found in images/ directory.")
            return None
        return random.choice(all_pngs)
    
    return random.choice(matching)

def create_message_image(message: str):
    # Create a blank white image for the e-Paper display.
    image = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    # Set a padding and define the maximum text width.
    padding = 20
    max_text_width = EPD_WIDTH - 2 * padding

    # Try to load a truetype font; fallback to default if unavailable.
    try:
        # You can adjust the font path and size as needed.
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except Exception as e:
        logging.warning("Could not load truetype font, using default font: " + str(e))
        font = ImageFont.load_default()

    # Manually wrap text based on pixel width.
    words = message.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}" if current_line else word
        line_width, _ = draw.textsize(test_line, font=font)
        if line_width <= max_text_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calculate total height of the text block.
    # Using font.getsize to estimate the height of a representative character.
    _, line_height = draw.textsize("A", font=font)
    total_text_height = line_height * len(lines)

    # Calculate starting y position to center text vertically.
    y = (EPD_HEIGHT - total_text_height) // 2

    # Draw each line centered horizontally.
    for line in lines:
        line_width, _ = draw.textsize(line, font=font)
        x = (EPD_WIDTH - line_width) // 2
        draw.text((x, y), line, font=font, fill=0)
        y += line_height

    return image

def main():
    logging.info("Initializing e-Paper display...")
    message_file = "/home/admin/message.txt"
    if os.path.exists(message_file):
        with open(message_file, "r") as f:
            message = f.read().strip()
        if message:
            logging.info("Custom message found. Displaying message: " + message)
            image = create_message_image(message)  
            epd = epd4in26.EPD()
            epd.init()
            epd.display(epd.getbuffer(image))
            epd.sleep()
            os.remove(message_file)
            return 
            
    epd = epd4in26.EPD()
    epd.init()

    update_count = get_update_count()
    
    # Only do a full clear occasionally
    if update_count % UPDATE_COUNT == 0:
        logging.info("Performing full screen clear to prevent ghosting...")
        epd.Clear()
    else:
        logging.info("Skipping full clear to reduce flashing...")

    image_file = pick_random_image_for_current_minute()
    if not image_file:
        logging.warning("No image to display.")
        return

    image_path = os.path.join(IMAGES_DIR, image_file)
    logging.info(f"Opening image: {image_path}")
    display_image = Image.open(image_path).convert("1")
    display_image = display_image.resize((EPD_WIDTH, EPD_HEIGHT))

    logging.info("Sending image to e-Paper display...")
    epd.display(epd.getbuffer(display_image))

    logging.info("Putting e-Paper display into sleep mode...")
    epd.sleep()

    # Save new update count
    save_update_count(update_count + 1)

if __name__ == "__main__":
    main()
