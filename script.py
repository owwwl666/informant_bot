import textwrap
import requests
import logging
import time
import telegram
import argparse
from environs import Env

logger = logging.getLogger('notice')


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )


def make_request_verified_works(dvmn_token: str, timestamp: float, url='https://dvmn.org/api/long_polling/'):
    """Делает запрос на проверенные работы.

    Возвращает словарь с данными о проверенной работе."""

    response = requests.get(
        url=url,
        params={'timestamp': timestamp},
        headers={'Authorization': f'Token {dvmn_token}'},
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def prepare_data_for_message(response: dict) -> str:
    """Подготавливает данные для отправки сообщения о результатах проверки.

    Возвращает итоговое сообщение."""

    notice = response['new_attempts'][0]
    lesson_title = notice['lesson_title']
    lesson_url = notice['lesson_url']
    is_negative = notice['is_negative']

    message = f'''
    У вас проверили работу  "{lesson_title}."
    
    {"К сожалению в работе нашлись ошибки." if is_negative
    else "Преподавателю все понравилось, можно приступать к следующему уроку!"}
        
    {lesson_url}'''

    return textwrap.dedent(message)


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

    dvmn_token = env.str("API_DEVMAN_TOKEN")

    bot = telegram.Bot(token=env.str('API_TELEGRAM_BOT_TOKEN'))
    log_bot = telegram.Bot(token=env.str('LOG_BOT_TOKEN'))

    logging.basicConfig(format="%(levelname)s::%(message)s")
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(
        bot=log_bot,
        chat_id=args.chat_id
    )
    )

    timestamp = None

    while True:
        try:
            verified_work = make_request_verified_works(
                dvmn_token=dvmn_token,
                timestamp=timestamp
            )

            if verified_work['status'] == 'timeout':
                timestamp = verified_work['timestamp_to_request']

            elif verified_work['status'] == 'found':
                timestamp = verified_work['last_attempt_timestamp']
                message = prepare_data_for_message(response=verified_work)
                bot.send_message(
                    chat_id=args.chat_id,
                    text=message
                )
        except requests.exceptions.ReadTimeout:
            logger.warning('Проверенных работ пока нет')
            continue
        except requests.exceptions.ConnectionError:
            logger.error('Отсутствует подключение к сети')
            time.sleep(5)
            continue
