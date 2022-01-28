# This is a sample Python script.
from cv2 import cv2
from os import listdir
from random import randint
from random import random
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

# Load config file.
from src.account_manager import go_to_account
from src.bot import bot_run, count_chest
from src.images_manager import load_images, positions

stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause


def to_set_accounts(accounts):
    result = dict()
    for i,k in enumerate(accounts):
        result[i] = {
            "name": "Chrome "+str(i),
            "chrome": k,
            "login": time.time(),
            "heroes": 0,
            "new_map": time.time(),
            "refresh_heroes": time.time(),
            "chests": {
                "brown": 99999
            }
    }
    return result





def main():
    """Main execution setup and loop"""
    # ==Setup==
    global hero_clicks
    global login_attempts
    global last_log_is_progress
    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()
    # time.sleep(7)

    t = c['time_intervals']
    # =========
    accounts = positions(images['chrome'], threshold=ct['chrome'])
    accounts = to_set_accounts(accounts)
    index = 0
    account = accounts[index % len(accounts)]
    go_to_account(account)
    while True:
        sys.stdout.flush()
        bot_run(account, t, images)
        count_chest(account)
        index +=1
        account = accounts[index % len(accounts)]
        if len(accounts) > 1: go_to_account(account)




if __name__ == '__main__':
    main()
