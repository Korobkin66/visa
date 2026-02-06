# -*- coding: utf8 -*-

import os
import time
import random
import platform
import logging
from datetime import datetime

import requests
from selenium import webdriver
# from selenium.webdriver.support import expected_conditions as EC 
# from selenium.webdriver.support.ui import WebDriverWait as Wait
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
file_log = logging.FileHandler("thecode.log")
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

console_out.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
console_out.setFormatter(formatter)

logger.addHandler(console_out)


USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
SCHEDULE = '71354735'

PUSH_TOKEN = os.getenv('PUSH_TOKEN')
PUSH_USER = os.getenv('PUSH_USER')

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

BOT_TOKEN = os.getenv("HTTP_API")
CHAT_ID = os.getenv("CHAT_ID")

REMOTE_URL = os.getenv('REMOTE_URL')

MY_SCHEDULE_DATE = "2025-10-27"  # 2025-12-02
MY_CONDITION = lambda month,day: int(month) == 11 and int(day) >= 5

SLEEP_TIME = 5   # recheck time interval
CHECK_INTERVAL = 600          # 10 минут
HEARTBEAT_INTERVAL = 14400

URL = "https://ais.usvisa-info.com/ru-kz/niv/users/sign_in"
DATE_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/days/108.json?appointments[expedite]=false" % SCHEDULE
TIME_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment/times/108.json?date=%%s&appointments[expedite]=false" % SCHEDULE
APPOINTMENT_URL = "https://ais.usvisa-info.com/en-ec/niv/schedule/%s/appointment" % SCHEDULE
HUB_ADDRESS = 'http://localhost:4444/wd/hub'
PAYMENT_URL = 'https://ais.usvisa-info.com/ru-kz/niv/schedule/71354735/payment'
EXIT = False


options = webdriver.ChromeOptions()

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')

options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")  # для работы с Chrome

options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-features=UseDBus")


def send_telegram_message(text: str):

    # url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # payload = {
    #     "chat_id": CHAT_ID,
    #     "text": text,
    #     "parse_mode": "HTML"}
    # response = requests.post(url, data=payload)
    # response.raise_for_status()

    try:
        if not text:
            return

        # Telegram ограничение ~4096 символов
        if len(text) > 3500:
            text = text[:3500] + "\n\n…(truncated)"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
        }

        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()

    except Exception as e:
        logger.error(f"Telegram error: {e}")

# def send(msg):
#     url = "https://api.pushover.net/1/messages.json"
#     data = {
#         "token": PUSH_TOKEN,
#         "user": PUSH_USER,
#         "message": msg
#     }
#     requests.post(url, data)


def get_drive():
    # local_use = platform.system() == 'Darwin' # (MacOS)
    local_use = platform.system() == 'Linux'  # (Linux/Ubuntu)
    if local_use:
        service = Service(executable_path='/usr/bin/chromedriver') 
        dr = webdriver.Chrome(service=service, options=options)
    else:
        dr = webdriver.Remote(command_executor=REMOTE_URL, options=options)

    return dr


def login():
    logger.info("getting driver")
    driver = get_drive()

    logger.info("login start")
    driver.get("https://ais.usvisa-info.com/ru-kz/niv/users/sign_in")
    time.sleep(5)

    do_login_action(driver)
    print_payment = get_payment(driver)
    logger.info(f'Контент функции get_payment: {print_payment}')
    driver.quit()
    if print_payment != 'В данный момент запись невозможна.':
        return print_payment


def do_login_action(driver):
    print("input email")
    html = driver.page_source

# Запись в файл
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(html)
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

    print("Login successfully! ")


def get_payment(driver):
    driver.get(PAYMENT_URL)
    time.sleep(random.randint(5, 9))
    content = driver.find_element(By.XPATH, '//*[@id="paymentOptions"]/div[2]/table/tbody/tr[1]/td[2]').text

    return content


if __name__ == "__main__":

    logger.info("parsing start")

    # создаёт сессию (при первом запуске Telegram попросит код из чата)
    # client = TelegramClient('my_session', API_ID, API_HASH)

    # def main():
    #     while True:
    #         # log_var = login()
    #         try:
    #             # log_var = await asyncio.to_thread(login)
    #             log_var = login()
    #             logger.info(f'Содержание функции login: {log_var}')
    #             print(log_var)
    #             if log_var:
    #                 message = "🎉 Найдены свободные слоты:\n\n"
    #                 message += "\n".join(log_var)
    #                 send_telegram_message(message)
    #                 logger.info('Сообщение было отправлено')
    #             now = datetime.now()
    #             if now.hour == 15 and now.minute == 0:
    #                 send_telegram_message('active')
    #         except Exception as e:
    #             print(e)
    #             send_telegram_message(f'Произошла ошибка {e}')
    #         time.sleep(CHECK_INTERVAL)

    def main():
        last_heartbeat = time.time()  # ← ВАЖНО

        while True:
            try:
                log_var = login()
                logger.info(f'Содержание функции login: {log_var}')

                if log_var:
                    message = "🎉 Найдены свободные слоты:\n\n"
                    message += str(log_var)
                    send_telegram_message(message)
                    logger.info('Сообщение было отправлено')

                # ❤️ heartbeat (жив ли процесс)
                now_ts = time.time()
                if now_ts - last_heartbeat > HEARTBEAT_INTERVAL:
                    send_telegram_message("✅ Visa watcher работает")
                    last_heartbeat = now_ts

            except Exception as e:
                logger.exception("Unhandled error in main loop")

                # ⚠️ никогда не падаем из-за Telegram
                try:
                    send_telegram_message(
                        "❌ Ошибка в Visa watcher\n"
                        f"{str(e)[:1000]}"
                    )
                except Exception:
                    pass

            time.sleep(CHECK_INTERVAL)


    main()