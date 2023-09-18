import requests
import logging
import time
import telegram
import argparse
from environs import Env


def get_last_timestamp(dvmn_token, url='https://dvmn.org/api/user_reviews/'):
    response = requests.get(
        url=url,
        headers={'Authorization': f'Token {dvmn_token}'}
    )
    return response.json()['results'][0]['timestamp']


def inform_verified_works(dvmn_token, chat_id, url='https://dvmn.org/api/long_polling/'):
    while True:
        try:
            response = requests.get(
                url=url,
                params={'timestamp': get_last_timestamp(dvmn_token)},
                headers={'Authorization': f'Token {dvmn_token}'},
                timeout=5
            )
            response.raise_for_status()

            notice = response.json()['new_attempts'][0]
            lesson_title = notice['lesson_title']
            lesson_url = notice['lesson_url']
            is_negative = notice['is_negative']

            bot.send_message(
                chat_id=chat_id,
                text=f'У вас проверили работу "{lesson_title}"\n\n'
                     f'{"К сожалению в работе нашлись ошибки." if is_negative else "Преподавателю все понравилось, можно приступать к следующему уроку!"}\n\n'
                     f'{lesson_url}'
            )
        except requests.exceptions.ReadTimeout:
            logger.warning('Проверенных работ пока нет')
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Отсутствует подключение к сети')
            time.sleep(5)
            continue


if __name__ == '__main__':
    env = Env()
    env.read_env()

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

    logger = logging.getLogger('logger')

    dvmn_token = env.str("API_DEVMAN_TOKEN")
    telegram_bot_token = env.str('API_TELEGRAM_BOT_TOKEN')
    chat_id = env.int('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(token=telegram_bot_token)

    inform_verified_works(
        dvmn_token=dvmn_token,
        chat_id=args.chat_id
    )