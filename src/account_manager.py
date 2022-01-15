import pyautogui

from src.images_manager import click_btn, move_to_with_randomness


def go_to_account(account):
    x, y, w, h = account["chrome"]
    pos_click_x = x + w / 2
    pos_click_y = y + h / 2
    move_to_with_randomness(pos_click_x, pos_click_y, 1)
    pyautogui.click()
    pass
