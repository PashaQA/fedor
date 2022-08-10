import json
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# ------------------------------------------------
# Настройки Федора
URL = 'https://bitrix.sbermarketing.ru/stream'

DAYS = [1, 2, 3, 4, 5]

HOUR_START = 17
MINUTE_START = 36

HOUR_END = 18
MINUTE_END = 56

CRED_PATH = 'cred.json'

DEBUG = False
DOCKER = True
# ------------------------------------------------


def start_driver():
    if DOCKER:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver


def go_to_index_page(driver):
    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError('Блэд чехол креды дай')

    with open(CRED_PATH) as file:
        cred = json.loads(file.read())

    driver.get(URL)

    # Вводим логин
    elem = driver.find_element(by=By.NAME, value='USER_LOGIN')
    elem.clear()
    elem.send_keys(cred['login'])

    # Вводим пароль
    elem = driver.find_element(by=By.NAME, value='USER_PASSWORD')
    elem.clear()
    elem.send_keys(cred['password'])

    # Сброс персональных данных
    cred = None

    # Клик по кнопке "Войти"
    driver.find_element(by=By.CLASS_NAME, value='login-btn').click()

    time.sleep(4)

    # Закрываем всплывающее окно, если оно есть
    try:
        driver.find_element(by=By.CLASS_NAME, value='popup-window-close-icon.popup-window-titlebar-close-icon').click()
    except Exception:
        pass

    time.sleep(1)

    # Клик по кнопке вызова модального окна старта/завершения работы
    driver.find_element(by=By.ID, value='timeman-status-block').click()


def click_button_start(driver):
    # Клик по кнопке старта работы
    try:
        driver.find_element(by=By.CLASS_NAME, value='ui-btn.ui-btn-success.ui-btn-icon-start').click()
    except Exception:
        print('Федор не нашел кнопку старта рабочего дня')


def click_button_end(driver):
    # Клик по кнопке завершения работы
    try:
        driver.find_element(by=By.CLASS_NAME, value='ui-btn.ui-btn-danger.ui-btn-icon-stop').click()
    except Exception:
        print('Федор не нашел кнопку завершения рабочего дня')


if __name__ == '__main__':
    print('Федор запущен')

    driver = None
    last_end_day = None
    last_start_day = None

    while True:
        now = datetime.now()

        if DEBUG or (
            now.isoweekday() in DAYS
            and now.hour == HOUR_START
            and now.minute == MINUTE_START
            and last_start_day != now.day
        ):
            print(f'Обнаружено совпадение условия старта работы, время "{now}".')
            try:
                # Открываем драйвер
                driver = start_driver()

                # Выполняем процесс
                go_to_index_page(driver)
                time.sleep(1)
                click_button_start(driver)

            except Exception as e:
                print(e.args[0])
                print(f'Ошибка в процессе старта работы. Время "{now}"')
            else:
                print(f'Процесс старта работы успешно завершен. Время {now}')
            finally:
                # Говорим, что сегодня кнопку старта работы нажимали,
                # чтобы сегодня больше не запускался процесс (анти спам)
                last_start_day = now.day

                # Закрываем драйвер
                if driver:
                    driver.close()

        elif DEBUG or (
            now.isoweekday() in DAYS and now.hour == HOUR_END and now.minute == MINUTE_END and last_end_day != now.day
        ):
            print(f'Обнаружено совпадение условия завершения работы, время "{now}".')
            try:
                # Открываем драйвер
                driver = start_driver()

                # Выполняем процесс
                go_to_index_page(driver)
                time.sleep(1)
                click_button_end(driver)

            except Exception as e:
                print(e.args[0])
                print(f'Ошибка в процессе завершения работы. Время "{now}"')
            else:
                print(f'Процесс завершения работы успешно завершен. Время {now}')
            finally:
                # Говорим, что сегодня кнопку завершения работы нажимали,
                # чтобы сегодня больше не запускался процесс (анти спам)
                last_end_day = now.day

                # Закрываем драйвер
                if driver:
                    driver.close()
