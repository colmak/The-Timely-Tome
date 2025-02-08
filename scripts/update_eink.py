#!/usr/bin/env python3
import os
os.environ["DISPLAY"] = ":0"
import random
import datetime
from PIL import Image
import logging
import time

#log_file = "/home/pi/eink_debug.log"
#logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#logging.debug("Running e-Paper update script...")
#logging.debug(f"Current environment variables: {os.environ}")

# Import Waveshare e-Paper driver
import sys
sys.path.append('/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib')  
sys.path.append('/home/admin/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd')  # Correct path to Waveshare drivers

import epd4in26  # Import the correct e-Paper display driver

# Set correct dimensions for 4.26-inch e-Paper display
EPD_WIDTH = 800  # Update to match epd4in26 specs
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

def main():
    logging.info("Initializing e-Paper display...")
    epd = epd4in26.EPD()
    epd.init()

    update_count = get_update_count()
    
    # Only do a full clear occasionally
    if update_count % UPDATE_COUNT == 0:
        logging.info("Performing full screen clear to prevent ghosting...")
        epd.init()
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
