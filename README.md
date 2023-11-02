# Описание

Скрипт запрашивает данные у Devman о свежих проверенных работах ученика и сообщает о результатах проверки ученику в созданный им телеграм бот.

# Установка зависимостей
Введите в терминале команду для установки необходимых пакетов и зависимостей:
```
pip install -r requirements.txt
```

# Переменные окружения

В скрипте используется две переменных окружения:

- API_DEVMAN_TOKEN=<ЛИЧНЫЙ ТОКЕН ПОЛЬЗОВАТЕЛЯ DEVMAN>
- API_TELEGRAM_BOT_TOKEN=<API ТОКЕН ТЕЛЕГРАМ БОТА>

# Запуск скрипта

При запуске скрипта необходимо передать один обязательный аргумент `chat_id` - ваш идентификатор в телеграм, для того чтобы бот мог сообщать вам о результатах проверки:

```
python script.py --chat_id <chat_id>
```

# Сценарий тестирования

Чтобы проверить реакцию сервера на запросы, нужно сначала отправить работу на проверку, а затем дождаться её проверки. Это можно сделать без участия преподавателя: отправьте любой урок на проверку и нажмите «Вернуть работу с проверки», бот пришлет вам сообщение с результатом проверки.

# Результат

![image](https://github.com/owwwl666/informant_bot/assets/131767856/9d04caa4-fe62-49d7-b3a5-9433542cedc0)
