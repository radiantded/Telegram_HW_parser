import logging
import os
import time

import requests
import telegram

from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
LOGGER = logging.getLogger(__name__)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    hw_status = homework.get('status')
    if homework_name is None or hw_status is None:
        return 'Нет данных'
    statuses = {
        'reviewing': 'Работа отправлена на проверку',
        'rejected': 'К сожалению в работе нашлись ошибки',
        'approved': ('Ревьюеру всё понравилось, '
                     'можно приступать к следующему уроку')
    }
    verdict = statuses.get(hw_status)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    timestamp = (current_timestamp if current_timestamp
                 is not None else int(time.time()))
    date = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            params=date, headers=headers
        )
        return homework_statuses.json()
    except Exception:
        LOGGER.exception('Ошибка')


def send_message(message, bot_client):
    LOGGER.info('Отправка сообщения')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    LOGGER.debug('Запуск бота')
    bot_client = telegram.Bot(TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client
                )
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )  # обновить timestamp
            time.sleep(1200)

        except Exception as error:
            LOGGER.error(error, exc_info=True)
            print('Произошел сбой в работе бота')
            send_message('Произошел сбой в работе бота', bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
