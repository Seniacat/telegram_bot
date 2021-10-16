from dotenv import load_dotenv
import logging
import os
import requests
import sys
import time
import telegram

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

ENV = {
    'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
    'TELEGRAM_TOKEN': TELEGRAM_TOKEN
}

RETRY_TIME = 60 * 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}

logging.basicConfig(
    format='%(asctime)s - %(lineno)d - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)


class StatusCodeNot200(Exception):
    """Исключение, вызываемое при коде ответа API, не равном 200."""

    def __init__(self, response):
        """Инициализатор."""
        self.response = response

    def __str__(self):
        """Вывод сообщения об ошибке."""
        return (f'Эндпойнт "{self.response.url} недоступен.'
                f'Код ответа API: {self.response.status_code}')


class KeyNotFound(Exception):
    """Исключение, вызываемое при отсутствии ожидаемых ключей в ответе API."""

    def __str__(self):
        """Вывод сообщения об ошибке."""
        return "Ожидаемые данные отсутствуют в ответе API"


class StatusError(Exception):
    """Исключение, вызываемое при недокументированном статусе работы."""

    def __init__(self, status):
        """Инициализатор."""
        self.status = status

    def __str__(self):
        """Вывод сообщения об ошибке."""
        return f'Недокументированный статус домашней работы: {self.status}'


def send_message(bot, message):
    """Функция отправки сообщений об изменении статуса в мессенджер."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот отправил сообщение "{message}"')
    except Exception:
        logging.error(
            f'Не удалось отправить сообщение "{message}".'
            'Сбой при отправке сообщения.'
        )


def get_api_answer(url, current_timestamp):
    """Функция отправки запросов к API."""
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        if homework_statuses.status_code != 200:
            raise StatusCodeNot200(homework_statuses)
    except Exception:
        raise StatusCodeNot200(homework_statuses)
    return homework_statuses.json()


def parse_status(homework):
    """Функция для анализа статуса домашнего задания в ответе API."""
    status = homework.get('status')
    try:
        verdict = HOMEWORK_STATUSES[status]
    except KeyError:
        raise StatusError(status)
    homework_name = homework.get('homework_name')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    """Функция проверки изменения статуса домашнего задания в ответе API."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        raise KeyNotFound
    if homeworks:
        return parse_status(homeworks[0])


def update_timestamp(response):
    """Функция обновления временной метки, отправляемой в запросе к API."""
    try:
        current_date = int(response['current_date'])
    except KeyError:
        raise KeyNotFound
    return current_date


def check_tokens():
    """Функция проверки наличия токенов."""
    for token in ENV:
        if ENV[token] is None:
            logging.critical(
                f'Отсутcтвует обязательная переменная окружения {token}'
                'Программа принудительно завершена'
            )
            exit()


def main():
    """Функция запуска бот-ассистента."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_error = ""
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(ENDPOINT, current_timestamp)
            message = check_response(response)
            current_timestamp = update_timestamp(response)
            if message:
                send_message(bot, message)
            time.sleep(RETRY_TIME)
        except (StatusCodeNot200, KeyNotFound, StatusError) as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if str(error) != previous_error:
                send_message(bot, message)
            previous_error = str(error)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
