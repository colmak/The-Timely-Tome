#!/usr/bin/env python3
import os
import random
import datetime
from PIL import Image
import logging

# If using Waveshare e-Paper, add the driver import
# e.g.:
#import sys
#sys.path.append('/home/pi/my-autoclock-repo/waveshare-libs') 
#import epd7in5_V2  # or your specific driver

logging.basicConfig(level=logging.INFO)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")
EPD_WIDTH = 800
EPD_HEIGHT = 480

def pick_random_image_for_current_minute():
    now = datetime.datetime.now()
    time_str = now.strftime("%H-%M")
    matching = []
    for fname in os.listdir(IMAGES_DIR):
        if fname.startswith(time_str) and fname.endswith(".png"):
            matching.append(fname)

    if not matching:
        # fallback to any image if no exact matches
        all_pngs = [f for f in os.listdir(IMAGES_DIR) if f.endswith(".png")]
        if not all_pngs:
            logging.warning("No PNG images found in images/ directory.")
            return None
        return random.choice(all_pngs)

    return random.choice(matching)

def main():
    # e.g. epd = epd7in5_V2.EPD()
    # epd.init()
    # epd.Clear()

    image_file = pick_random_image_for_current_minute()
    if not image_file:
        logging.warning("No image to display.")
        return

    image_path = os.path.join(IMAGES_DIR, image_file)
    logging.info("Displaying: %s", image_path)

    display_image = Image.open(image_path).convert("1")
    display_image = display_image.resize((EPD_WIDTH, EPD_HEIGHT))

    # epd.display(epd.getbuffer(display_image))
    # epd.sleep()

if __name__ == "__main__":
    main()
