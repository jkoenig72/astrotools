#!/usr/bin/python3
import os
import calendar
import time
import subprocess
import logging
import requests  # Import requests for HTTP POST

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

cmd1 = ['runuser', '-l', 'fritz', '-c', 'systemctl --user restart indi-allsky']
cmd2 = ['systemctl', 'restart', 'indiserver']

ct = 180  # Allowed time difference in seconds for primary check (3 minutes)
extended_ct = 600  # Extended time difference in seconds for secondary check (10 minutes)
image = '/var/www/html/allsky/images/latest.jpg'

remote_pc_url = 'http://192.168.10.43:8624/api/system/reboot'  # URL to reboot remote PC

logging.info("Allowed difference in sec. for primary check: " + str(ct))
logging.info("Allowed difference in sec. for extended check: " + str(extended_ct))

def reboot_remote_pc():
    """Function to reboot the remote PC."""
    try:
        response = requests.post(remote_pc_url)
        if response.status_code == 200:
            logging.info("Successfully sent reboot command to remote PC.")
        else:
            logging.error(f"Failed to send reboot command to remote PC. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending reboot command to remote PC: {e}")

def reboot_local_machine():
    """Function to reboot the local machine."""
    try:
        subprocess.run(['sudo', 'reboot'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to reboot local machine: {e}")

try:
    logging.info(f"Inial wait after start - 10 min") 
    time.sleep(600)
    while True:
        try:
            f = os.path.getmtime(image)
        except FileNotFoundError:
            logging.error(f"Image file not found: {image}")
            time.sleep(30)
            continue
        
        c = calendar.timegm(time.gmtime())
        d = int(c - f)

        if d > extended_ct:
            # Extended check: image is too old, reboot both machines
            logging.info(f"Image too old (more than {extended_ct} sec.), rebooting remote and local machines.")
            reboot_remote_pc()
            time.sleep(10)  # Give a small delay before rebooting the local machine
            reboot_local_machine()
            break  # Exit the loop since the local machine will be rebooted

        elif d > ct:
            # Primary check: image is older than allowed threshold, restart service
            logging.info(f"Image too old, {d} sec., restarting service!")
            subprocess.run(cmd1)
            # subprocess.run(cmd2)
            time.sleep(240)  # Sleep for 4 minutes after restarting service
        
        else:
            logging.info(f"Image is {d} sec. old - ok.")
        
        time.sleep(30)
except KeyboardInterrupt:
    logging.info("Watchdog terminated by user.")

