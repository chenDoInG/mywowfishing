# _*_coding:utf-8_*_
# Author      :ories
# File_Name   :fishing.py
# Create_Date :2020-02-26 19:31
# Description :wow fishing script
# IDE         :PyCharm
import time

from pymouse import PyMouse
from pykeyboard import PyKeyboard
import pyscreenshot as ImageGrab
import cv2
from mic import Recorder

keyboard = PyKeyboard()
mouse = PyMouse()
record = Recorder()


def get_start_point():
    print("Checking screen size")
    img = ImageGrab.grab()

    print('img.size', img.size)

    screen_size = img.size

    start_point = (screen_size[0] / 2 * 0.2, screen_size[1] / 2 * 0.1)
    # in my screen need to divide 2, you can check on your screen. I don't know why, but I'm glad someone could tell me
    end_point = (screen_size[0] / 2 * 0.8, screen_size[1] / 2 * 0.7)
    print("Screen size is ", str(screen_size))
    return [start_point, end_point]


def send_float():
    print('Sending float')
    keyboard.tap_key('1', 1)
    print('Float is sent, waiting animation')
    time.sleep(2)


def make_screenshot(mini_screen):
    [screen_start_point, screen_end_point] = mini_screen
    size = (int(screen_start_point[0]), int(screen_start_point[1]), int(screen_end_point[0]), int(screen_end_point[1]))
    print('make screenshot', size)
    screenshot = ImageGrab.grab(bbox=size)
    screenshot_name = 'var/fishing_session' + '.png'
    screenshot.save(screenshot_name)
    return screenshot_name


def move_mouse(place, screen_start_point):
    # print()
    [x, y] = place

    location_x = int(screen_start_point[0])
    location_y = int(screen_start_point[1])

    # add (40,30) due to the feather of the float
    lx = location_x + x + 40
    ly = location_y + y + 30
    print('move_mouse to ', [lx, ly])
    mouse.move(lx, ly)
    return [lx, ly]


def find_float(screenshot):
    print('Looking for float')

    # 加载原始的rgb图像
    screenshot_rgb = cv2.imread(screenshot)
    # 创建一个原始图像的灰度版本，所有操作在灰度版本中处理，然后在RGB图像中使用相同坐标还原
    screenshot_gray = cv2.cvtColor(screenshot_rgb, cv2.COLOR_BGR2GRAY)

    # 加载将要搜索的图像模板
    img_2_search = cv2.imread('var/fishing_float.png', 0)

    height, width = img_2_search.shape[:2]
    size = (int(width * 0.5), int(height * 0.5))
    img_2_search = cv2.resize(img_2_search, size, interpolation=cv2.INTER_AREA)

    # 记录图像模板的尺寸
    w, h = img_2_search.shape[::-1]
    res = cv2.matchTemplate(screenshot_gray, img_2_search, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    return max_loc[0], max_loc[1]


def waiting_for_bite_util_timeout():
    return record.listen()


def fishing(mini_screen):
    print('start fishing')
    send_float()
    screenshot = make_screenshot(mini_screen)
    float_in_screenshot = find_float(screenshot)
    print('find float in screenshot', float_in_screenshot)
    float_in_screen = move_mouse(float_in_screenshot, mini_screen[0])

    if not waiting_for_bite_util_timeout():
        print('If we didn\' hear anything, lets try again')

    mouse.click(float_in_screen[0], float_in_screen[1], 2)
    time.sleep(1)


def hang_up():
    time.sleep(10)
    [screen_start_point, screen_end_point] = get_start_point()
    mini_screen = [screen_start_point, screen_end_point]
    n = 1
    while True:
        fishing(mini_screen)
        # keyboard.press_key("command")
        # keyboard.tap_key("Tab", n=n)
        # keyboard.release_key("command")
        # n = n % 3 + 1
        # time.sleep(2)


1
if __name__ == '__main__':
    hang_up()
