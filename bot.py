import telebot
import schedule
import time
from datetime import datetime

#  токен
TOKEN = 'my token'

time.sleep(5)

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения новостей
news = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который добавляет новости в нужное время. Напиши /addnews, чтобы добавить новость.")

# Обработчик команды /addnews
@bot.message_handler(commands=['addnews'])
def add_news(message):
    bot.reply_to(message, "Введите текст новости:")
    bot.register_next_step_handler(message, get_news_text)

# Получение текста новости от пользователя
def get_news_text(message):
    news_text = message.text
    bot.reply_to(message, "Когда вы хотите опубликовать эту новость? Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ (например, 27.01.2025 14:30):")
    news[message.chat.id] = {'text': news_text}  # Сохраняем текст новости

    # Регистрация следующего шага для ввода даты и времени публикации
    bot.register_next_step_handler(message, get_news_datetime)

# Получение даты и времени публикации
def get_news_datetime(message):
    try:
        # Парсим дату и время из сообщения
        publish_datetime = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        # Сохраняем дату и время публикации
        news[message.chat.id]['datetime'] = publish_datetime
        bot.reply_to(message, f"Новость запланирована на {publish_datetime.strftime('%d.%m.%Y %H:%M')}. Спасибо!")

        # Добавляем задачу в расписание
        schedule_task(publish_datetime, message.chat.id)

    except ValueError:
        # Если формат даты и времени некорректный, просим пользователя повторить ввод
        bot.reply_to(message, "Неверный формат. Пожалуйста, введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ (например, 27.01.2025 14:30):")
        bot.register_next_step_handler(message, get_news_datetime)

# Настраиваем задачу в расписании
def schedule_task(publish_datetime, chat_id):
    now = datetime.now()
    delay = (publish_datetime - now).total_seconds()
    if delay > 0:
        # Планируем задачу с задержкой
        schedule.every(delay).seconds.do(publish_news, chat_id).tag(f"news_{chat_id}")
    else:
        bot.send_message(chat_id, "Указанная дата и время уже прошли. Попробуйте снова.")
        del news[chat_id]  # Удаляем ошибочную запись

# Функция для публикации новости
def publish_news(chat_id):
    if chat_id in news:
        content = news[chat_id]
        bot.send_message(chat_id, f"📰 Новость: {content['text']}")
        del news[chat_id]  # Удаляем новость после публикации

# Запуск расписания
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск бота
if __name__ == "__main__":
    import threading
    # Запускаем бота в отдельном потоке
    threading.Thread(target=bot.polling).start()
    # Запускаем расписание
    run_schedule()
