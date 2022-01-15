import time
from random import random, randint

import numpy as np
import pyautogui
import yaml
import mss

import sys
from os import listdir
from cv2 import cv2

from src.logger import logger

stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
images = []
login_attempts = 0


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # Grab the data
        return sct_img[:, :, :3]


def positions(target, threshold, img=None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


def move_to_with_randomness(x, y, t):
    pyautogui.moveTo(addRandomness(x, 10), addRandomness(y, 10), t + random() / 2)


def click_btn(img, timeout=3, threshold = ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    start = time.time()
    has_timed_out = False
    while (not has_timed_out):
        matches = positions(img, threshold=threshold)

        if (len(matches) == 0):
            has_timed_out = time.time() - start > timeout
            continue
        for match in matches:
            x, y, w, h = match
            pos_click_x = x + w / 2
            pos_click_y = y + h / 2
            move_to_with_randomness(pos_click_x, pos_click_y, 1)
            pyautogui.click()
        return True

    return False
