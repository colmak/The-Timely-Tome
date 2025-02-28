![clock png](https://github.com/user-attachments/assets/89707382-4ea3-46ad-b2e0-475735db5f92)
# The Timely Tome: E-Ink Book Quote Clock

**The Timely Tome** is a Raspberry Pi–based eInk “clock” that displays pre-generated quotes or excerpts corresponding to the current time.  
Every minute, the Pi updates the eInk screen with a random image that matches (or approximates) the time of day, offering a snippet of literature or wisdom to match that minute.

## Features

- **Time-Based Quotes**: Thousands of pre-generated `.png` files, each tagged with a specific time. 
- **eInk Display**: Uses a Waveshare (or similar) ePaper HAT for a crisp, low-power reading experience.  
- **Minute-by-Minute Updates**: A cron job triggers the script every minute to pick and display the correct image.  
- **Easy to Deploy**: Clone this repo, install dependencies, set your cron, and let the Pi handle everything.

---

## Repository Layout

```
/
├── images/
│   ├── 00-00_1.png
│   ├── 08-05_1.png
│   └── ... (all other time-based PNGs)
├── quote stuff/
│   └── all the fun stuff for quotes
├── scripts/
│   ├── update_eink.py     # Main script to display the image
│   └── imagegen.py        # Create the images from the scripts
├── cronjob.md             # Detailed instructions on cron job setup
├── requirements.txt       # Python dependency list
└── README.md              # This file
```

---

## Quick Start

1. **Clone** the repo onto your Raspberry Pi:

   ```bash
   cd /home/pi
   git clone https://github.com/colmak/the-timely-tome.git
   cd the-timely-tome
   and install requirements.txt
   ```

2. **Connect & Test**  
   - Make sure your eInk display is connected and SPI is enabled.  
   - Run the update script manually:
     ```bash
     python3 scripts/update_eink.py
     ```
   - You should see the display refresh with a PNG chosen from the `images` directory.

3. **Set Up Cron**  
   See **CRON_SETUP.md** for step-by-step instructions on running `update_eink.py` **every minute**.

---

## Generating Quotes/Images

- If you have a separate script that **generates** the images (like `imagegen.py`), you can place it in a separate directory or keep it local.  
- Once you’ve generated the `.png` files, just drop them into the `images/` folder.  
- Make sure the naming convention is `HH-MM_#`, e.g. `08-05_1.png`, `08-05_2.png`.  
- The main update script uses that pattern to find time-specific images.

---

## Troubleshooting

1. **Display not updating**:
   - Check your wiring and the ePaper driver installation.  
   - Verify the cron job: `crontab -l` to see if your line is there.  
   - Check logs if you’re redirecting output: `cat /home/pi/eink.log`.

2. **Performance**:
   - eInk refresh rates can be slow or cause flicker. Adjust the script timing or partial refresh if your display supports it.
