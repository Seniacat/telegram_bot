# Telegram bot
## Описание:
Проект сервиса telegram_bot, работающий с API сервиса Практикум.Домашка.

Даёт возможность:
- делать запросы к базе данных с выбранной периодичностью, получать статус проверки домашней работы
- получать оповещение об обновлении статуса проверки работы в Телеграмме
- получать оповещение об ошибках в работе бота в Телеграмме 

В проекте применяется логирование, обработка исключений при доступе к внешним сетевым ресурсам, конфиденциальные данные хранятся в пространстве переменных окружения.

## Системные требования
- Python 3.7+
- Works on Linux, Windows, macOS

## Используемые технологии:
- pytest==6.2.1
- python-dotenv==0.13.0
- python-telegram-bot==12.7
- requests==2.23.0
- telegram==0.0.1

## Запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Seniacat/telegram_bot.git
```
```
cd telegram_bot
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate (Mac OS, Linux) или source venv/Scripts/activate (Win10)
```
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
В основной директории добавьте файл .env, в котором укажите свои ключи для Praktikum и Telegram.

- PRAKTIKUM_TOKEN =
- TELEGRAM_TOKEN =
- TELEGRAM_CHAT_ID =

