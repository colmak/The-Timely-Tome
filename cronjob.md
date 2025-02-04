# Cron Job Setup

**Purpose**: Automatically run `update_eink.py` every minute so the eInk display updates with a new image.

## 1. Prerequisites

- You have **Python 3** and necessary dependencies installed.  
- You have **cloned** this repository onto your Pi

## 2. Make the Script Executable (Optional)

If the script isn’t already marked as executable, run:

```bash
chmod +x /home/pi/my-autoclock-repo/scripts/update_eink.py
```

*(This step isn’t strictly required, but is often helpful.)*

## 3. Edit the Crontab

1. Open the crontab editor:

   ```bash
   crontab -e
   ```

2. Add a new line at the bottom to run `update_eink.py` **every minute**:

   ```cron
   * * * * * /usr/bin/python3 /home/pi/my-autoclock-repo/scripts/update_eink.py >> /home/pi/eink.log 2>&1
   ```

   - `* * * * *` indicates the job will run every minute of every hour, every day.  
   - Adjust the paths if necessary:
     - `/usr/bin/python3` might be `/usr/bin/python` or `/usr/local/bin/python3` on some systems.  
     - `/home/pi/my-autoclock-repo/scripts/update_eink.py` is the full path to your script.  
   - `>> /home/pi/eink.log 2>&1` sends **all output (stdout + stderr)** to `eink.log` so you can later check it.

3. **Save and exit** the crontab editor. On most systems with **nano**, press `Ctrl+O` to write out, then `Ctrl+X` to exit.

## 4. Verify Cron is Running

- Cron typically starts automatically at boot. Check its status with:
  ```bash
  systemctl status cron
  ```
  You should see something like **“active (running)”**.

- Wait a minute or two, then **check your log file**:
  ```bash
  cat /home/pi/eink.log
  ```
  If the script is working, you’ll see log entries or any warnings/errors there.

## 5. (Optional) Reboot and Confirm

Reboot your Pi:

```bash
sudo reboot
```

Once it restarts, cron will continue running every minute. You can again look at `eink.log` to see if it’s updating and confirm the eInk display is refreshing as expected.

---

### Common Issues

- **No images displayed**: Verify your `update_eink.py` script correctly points to the directory of images (e.g., `images/`).  
- **Permission Denied**: Ensure the script is executable or specify `python3 <script>` explicitly as shown above.  
- **Wrong python path**: If you’re using a virtual environment, you may need the full path to that environment’s Python (`/home/pi/.venv/bin/python3`).  
- **Script not running**: Make sure you used the correct absolute path in your crontab line. Also ensure you pressed the right keys to save in `nano`.  

With that, your Raspberry Pi will automatically call the script **every minute**, updating the display seamlessly.