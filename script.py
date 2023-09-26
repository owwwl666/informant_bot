import textwrap

import requests
import logging
import time
import telegram
import argparse
from environs import Env

logger = logging.getLogger('notice')


def makes_request(dvmn_token: str, timestamp=None, url='https://dvmn.org/api/long_polling/'):
    """Делает запрос о статусе проверенных работ."""

    response = requests.get(
        url=url,
        params={'timestamp': timestamp},
        headers={'Authorization': f'Token {dvmn_token}'},
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def get_information(response: dict) -> tuple:
    """Получает данные о работе из запроса."""
    notice = response['new_attempts'][0]
    lesson_title = notice['lesson_title']
    lesson_url = notice['lesson_url']
    is_negative = notice['is_negative']
    return lesson_title, lesson_url, is_negative


def sends_message(chat_id: int, lesson_title: str, lesson_url: str, is_negative: bool) -> None:
    """Отправляет в бот сообщение с результатами проверки."""

    message = f'''
    У вас проверили работу  "{lesson_title}."
    
    {"К сожалению в работе нашлись ошибки." if is_negative
    else "Преподавателю все понравилось, можно приступать к следующему уроку!"}
        
    {lesson_url}'''

    bot.send_message(
        chat_id=chat_id,
        text=textwrap.dedent(message)
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()

    logger.setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(
        description='Скрипт запрашивает данные у Devman о свежих проверенных работах ученика'
                    'И сообщает о результатах проверки ученику в созданный им телеграм бот')
    parser.add_argument(
        '--chat_id',
        type=int,
        required=True,
        help='Идентификатор пользователя в телеграм'
    )
    args = parser.parse_args()

    dvmn_token = env.str("API_DEVMAN_TOKEN")
    telegram_bot_token = env.str('API_TELEGRAM_BOT_TOKEN')

    bot = telegram.Bot(token=telegram_bot_token)

    while True:
        try:
            response = makes_request(dvmn_token=dvmn_token)

            if response['status'] == 'timeout':
                response = makes_request(dvmn_token=dvmn_token, timestamp=response['timestamp_to_request'])

            lesson_title, lesson_url, is_negative = get_information(response)
            sends_message(
                chat_id=args.chat_id,
                lesson_title=lesson_title,
                lesson_url=lesson_url,
                is_negative=is_negative
            )
        except requests.exceptions.ReadTimeout:
            logger.warning('Проверенных работ пока нет')
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Отсутствует подключение к сети')
            time.sleep(5)
            continue
