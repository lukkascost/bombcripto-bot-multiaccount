import time
from random import random, randint

import numpy as np
import pyautogui
import yaml
import mss

from src.images_manager import addRandomness, move_to_with_randomness, printSreen, positions, click_btn
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


def count_chest(account):
    buttons = positions(images['brown-chest'], threshold=ct['brown-chest'])
    new_value = len(buttons)

    if (new_value +1) > account['chests']['brown']:
        sendAllHeroesToWork(images, ct)
    account['chests']['brown'] = len(buttons)


def bot_run(account, t , img):
    global images
    images = img
    now = time.time()
    logger('Change to account '+str(account))
    if now - account["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
        account["heroes"] = now
        account["refresh_heroes"] = now
        refreshHeroes()
    else:
        logger('🏢 No time to seach for work! '+ str(account))

    if now - account["login"] > addRandomness(t['check_for_login'] * 60):
        sys.stdout.flush()
        account["login"] = now
        login()
    else:
        logger('🏢 No time for login! '+  str(account))

    if now - account["new_map"] > t['check_for_new_map_button']:
        account["new_map"] = now

        if click_btn(images['new-map']):
            sendAllHeroesToWork(images, ct)
            account["heroes"] = now
            account["refresh_heroes"] = now
            account['chests']['brown'] = 99999
    else:
        logger('🏢 No time to seach for new map! '+  str(account))

    if now - account["refresh_heroes"] > addRandomness(t['refresh_heroes_positions'] * 60):
        account["refresh_heroes"] = now
        refreshHeroesPositions()
    else:
        logger('🏢 No time refresh heroes position! '+  str(account))
    sys.stdout.flush()




def sendAllHeroesToWork(images, ct):
    logger('🏢 Search for heroes to work')
    time.sleep(5)
    goToHeroes()
    click_btn(images['go-work-all'], threshold=ct['go_to_work_all_btn'])
    goToGame()


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


def show(rectangles, img = None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printSreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)


def scroll():

    commoms = positions(images['commom-text'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]
#
    move_to_with_randomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')


def click_buttons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        move_to_with_randomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickGreenBarButtons():
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 120

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))


    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' % len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        move_to_with_randomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        # hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)

def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        move_to_with_randomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def goToHeroes():
    if click_btn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    #TODO tirar o sleep quando colocar o pulling
    time.sleep(1)
    click_btn(images['hero-icon'])
    time.sleep(randint(1,3))

def goToGame():
    # in case of server overload popup
    click_btn(images['x'])
    # time.sleep(3)
    click_btn(images['x'])

    click_btn(images['treasure-hunt-icon'])

def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    click_btn(images['go-back-arrow'])
    click_btn(images['treasure-hunt-icon'])

    # time.sleep(3)
    click_btn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if click_btn(images['connect-wallet'], timeout = 2):
        logger('🎉 Connect wallet button detected, logging in!')
        login_attempts = login_attempts + 1
        #TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

    if click_btn(images['select-wallet-2'], timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if click_btn(images['treasure-hunt-icon'], timeout = 15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        return
        # click ok button

    if not click_btn(images['select-wallet-1-no-hover'], ):
        if click_btn(images['select-wallet-1-hover'], threshold = ct['select_wallet_buttons'] ):
            pass
            # o ideal era que ele alternasse entre checar cada um dos 2 por um tempo
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)
    else:
        pass
        # print('sleep in case there is no metamask text removed')
        # time.sleep(20)

    if click_btn(images['select-wallet-2'], timeout = 20):
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        # time.sleep(25)
        if click_btn(images['treasure-hunt-icon'], timeout=25):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        # time.sleep(15)

    if click_btn(images['ok'], timeout=5):
        pass
        # time.sleep(15)
        # print('ok button clicked')


def refreshHeroes():
    logger('🏢 Search for heroes to work')

    goToHeroes()

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts >0):
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons()
        else:
            buttonsClicked = click_buttons()

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 heroes sent to work')
    goToGame()