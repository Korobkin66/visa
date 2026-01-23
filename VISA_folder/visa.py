# -*- coding: utf8 -*-

import time
import json
import random
import platform
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from telethon import TelegramClient, utils, types

import logging
import asyncio
import os

# 8395673645:AAE2Ku-wDhM_RMrwqkZEHfF58vefm6m5eQw

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
# добавляем поток вывода в файл
file_log = logging.FileHandler("thecode.log")
# и вывод в консоль
console_out = logging.StreamHandler()

# указываем эти два потока в настройках логгера
logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

console_out.setLevel(logging.DEBUG)

# Создаём форматтер с временем
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
console_out.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(console_out)


USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
SCHEDULE = '71354735'

PUSH_TOKEN = os.getenv('PUSH_TOKEN')
PUSH_USER = os.getenv('PUSH_USER')

MY_SCHEDULE_DATE = "2025-10-27"  # 2025-12-02
MY_CONDITION = lambda month,day: int(month) == 11 and int(day) >= 5

SLEEP_TIME = 5   # recheck time interval

URL = "https://ais.usvisa-info.com/ru-kz/niv/users/sign_in"
DATE_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/days/108.json?appointments[expedite]=false" % SCHEDULE
TIME_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/times/108.json?date=%%s&appointments[expedite]=false" % SCHEDULE
APPOINTMENT_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment" % SCHEDULE
HUB_ADDRESS = 'http://localhost:4444/wd/hub'
PAYMENT_URL = 'https://ais.usvisa-info.com/ru-kz/niv/schedule/71354735/payment'
EXIT = False

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')


options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")  # для работы с Chrome

options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# REMOTE_URL = "https://chrome.browserless.io/webdriver?token=2TNibLG6T6LLHpq94c41ab667ecb4d15c528c4598a9dcdfcb"
REMOTE_URL = os.getenv('REMOTE_URL')


def send(msg):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSH_TOKEN,
        "user": PUSH_USER,
        "message": msg
    }
    requests.post(url, data)


def get_drive():
    # local_use = platform.system() == 'Darwin' # (MacOS)
    local_use = platform.system() == 'Linux'  # (Linux/Ubuntu)
    if local_use:
        dr = webdriver.Chrome()
    else:
        dr = webdriver.Remote(command_executor=REMOTE_URL, options=options)

    return dr


def login():
    driver = get_drive()

    # Bypass reCAPTCHA
    logger.info("login start")
    driver.get("https://ais.usvisa-info.com/ru-kz/niv/users/sign_in")
    time.sleep(1)

    do_login_action(driver)
    print_payment = get_payment(driver)
    logger.info(f'Контент функции get_payment: {print_payment}')
    driver.close()
    if print_payment != 'В данный момент запись невозможна.':
        return print_payment


def do_login_action(driver):
    print("input email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    print("input pwd")
    pw = driver.find_element(By.ID, 'user_password')
    pw.send_keys(PASSWORD) 
    time.sleep(random.randint(1, 3))

    print("click privacy")
    box = driver.find_element(By.CLASS_NAME, 'icheckbox')
    box .click()
    time.sleep(random.randint(1, 3))

    print("commit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    # Wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Continue')]")))
    print("Login successfully! ")


def get_payment(driver):
    driver.get(PAYMENT_URL)
    time.sleep(random.randint(1, 3))
    content = driver.find_element(By.XPATH, '//*[@id="paymentOptions"]/div[2]/table/tbody/tr[1]/td[2]').text

    return content


if __name__ == "__main__":

    logger.info("parsing start")
    # retry_count = 0
    real_id, peer_type = utils.resolve_id(-1003267457372)

    channel = '-1003267457372'

    # создаёт сессию (при первом запуске Telegram попросит код из чата)
    client = TelegramClient('my_session', API_ID, API_HASH)

    async def main():
        while True:
            # log_var = login()
            try:
                log_var = await asyncio.to_thread(login)
                logger.info(f'Содержание функции login: {log_var}')
                if log_var:
                    await client.send_message(types.PeerChannel(real_id), log_var)
                    logger.info('Сообщение было отправлено')
            except Exception as e:
                await client.send_message(types.PeerChannel(real_id),
                                          f'Произошла ошибка {e}')
            time.sleep(600)

    with client:
        client.loop.run_until_complete(main())
