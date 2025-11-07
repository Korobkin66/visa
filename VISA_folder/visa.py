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

# добавляем поток вывода в файл
file_log = logging.FileHandler("thecode.log")
# и вывод в консоль
console_out = logging.StreamHandler()

# указываем эти два потока в настройках логгера
logging.basicConfig(handlers=(file_log, console_out), level=logging.DEBUG)


USERNAME = 'doner66@gmail.com'
PASSWORD = 'Al89086307525Zx!'
SCHEDULE = '71354735'

PUSH_TOKEN = '<my push token>'
PUSH_USER = 'uhyji9ppjdhkfx25grddjjeg1c9mjx'

MY_SCHEDULE_DATE = "2025-10-27"  # 2025-12-02
# MY_CONDITION = lambda month,day: int(month) == 11 or (int(month) == 12 and int(day) <=5)
MY_CONDITION = lambda month,day: int(month) == 11 and int(day) >= 5

SLEEP_TIME = 5   # recheck time interval

URL = "https://ais.usvisa-info.com/ru-kz/niv/users/sign_in"
DATE_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/days/108.json?appointments[expedite]=false" % SCHEDULE
TIME_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/times/108.json?date=%%s&appointments[expedite]=false" % SCHEDULE
APPOINTMENT_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment" % SCHEDULE
HUB_ADDRESS = 'http://localhost:4444/wd/hub'
PAYMENT_URL = 'https://ais.usvisa-info.com/ru-kz/niv/schedule/71354735/payment'
EXIT = False

API_ID = '23238237'
API_HASH = 'c9a677eb94e21ed0b889e426fa19180b'


# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_SHIM', None)
# browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=chrome_options)


options = webdriver.ChromeOptions()
options.add_argument("--headless")

REMOTE_URL = "https://chrome.browserless.io/webdriver?token=2TNibLG6T6LLHpq94c41ab667ecb4d15c528c4598a9dcdfcb"

driver = webdriver.Remote(
    command_executor=REMOTE_URL,
    options=options
)

# driver = webdriver.Remote(
#     command_executor='https://chrome.browserless.io/webdriver?token=<YOUR_TOKEN>',
#     options=options
# )


def send(msg):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSH_TOKEN,
        "user": PUSH_USER,
        "message": msg
    }
    requests.post(url, data)


def get_drive():
    local_use = platform.system() == 'Darwin'
    if local_use:
        dr = webdriver.Chrome()
    else:
        dr = webdriver.Remote(command_executor=HUB_ADDRESS, 
                              desired_capabilities=DesiredCapabilities.CHROME)
    return dr
    # dr = webdriver.Chrome()
    # return dr

# driver = get_drive()


def login():
    # Bypass reCAPTCHA
    logging.info("login start")
    driver.get("https://ais.usvisa-info.com/ru-kz/niv/users/sign_in")
    time.sleep(1)

    do_login_action()
    print_payment = get_payment()
    logging.info(f'Контент функции get_payment: {print_payment}')
    if print_payment != 'В данный момент запись невозможна.':
        return print_payment


def do_login_action():
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


def get_payment():
    driver.get(PAYMENT_URL)
    time.sleep(random.randint(1, 3))
    # if not is_logined():
    #     login()
    #     return get_date()
    # else:
    content = driver.find_element(By.XPATH, '//*[@id="paymentOptions"]/div[2]/table/tbody/tr[1]/td[2]').text
    # date = json.loads(content)
    return content


def get_date():
    driver.get(DATE_URL)
    if not is_logined():
        login()
        return get_date()
    else:
        content = driver.find_element_by_tag_name('pre').text
        date = json.loads(content)
        return date


def get_time(date):
    time_url = TIME_URL % date
    driver.get(time_url)
    content = driver.find_element_by_tag_name('pre').text
    data = json.loads(content)
    time = data.get("available_times")[-1]
    print("Get time successfully!")
    return time


def reschedule(date):
    global EXIT
    print("Start Reschedule")

    time = get_time(date)
    driver.get(APPOINTMENT_URL)

    data = {
        "utf8": driver.find_element_by_name('utf8').get_attribute('value'),
        "authenticity_token": driver.find_element_by_name('authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element_by_name('confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element_by_name('use_consulate_appointment_capacity').get_attribute('value'),
        "appointments[consulate_appointment][facility_id]": "108",
        "appointments[consulate_appointment][date]": date,
        "appointments[consulate_appointment][time]": time,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "Referer": APPOINTMENT_URL,
        "Cookie": "_yatri_session=" + driver.get_cookie("_yatri_session")["value"]
    }
    
    r = requests.post(APPOINTMENT_URL, headers=headers, data=data)
    if (r.text.find('Successfully Scheduled') != -1):
        print("Successfully Rescheduled")
        send("Successfully Rescheduled")
        EXIT = True
    else:
        print("ReScheduled Fail")
        send("ReScheduled Fail")


def is_logined():
    content = driver.page_source
    if (content.find("error") != -1):
        return False
    return True


def print_date(dates):
    for d in dates:
        print("%s \t business_day: %s" %(d.get('date'), d.get('business_day')))
    print()


last_seen = None


def get_available_date(dates):
    global last_seen

    def is_earlier(date):
        return datetime.strptime(MY_SCHEDULE_DATE, "%Y-%m-%d") > datetime.strptime(date, "%Y-%m-%d")

    for d in dates:
        date = d.get('date')
        if is_earlier(date) and date != last_seen:
            _, month, day = date.split('-')
            if (MY_CONDITION(month, day)):
                last_seen = date
                return date


def push_notification(dates):
    msg = "date: "
    for d in dates:
        msg = msg + d.get('date') + '; '
    send(msg)


if __name__ == "__main__":

    logging.info("parsing start")
    # retry_count = 0
    real_id, peer_type = utils.resolve_id(-1003267457372)

    channel = '-1003267457372'

    # создаёт сессию (при первом запуске Telegram попросит код из чата)
    client = TelegramClient('my_session', API_ID, API_HASH)

    async def main():
        # log_var = login()
        log_var = await asyncio.to_thread(login)
        logging.info(f'Содержание функции login: {log_var}')
        if log_var:
            await client.send_message(types.PeerChannel(real_id), log_var)
            logging.info('Сообщение было отправлено')

    with client:
        client.loop.run_until_complete(main())

