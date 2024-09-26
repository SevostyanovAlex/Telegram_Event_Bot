import os
import sqlite3
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота и ID чата из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))

updater = Updater(token=TELEGRAM_TOKEN)

# Хранение состояния разговора и ответов пользователей
conversation_state = {}
user_responses = {}


def create_connection():
    """Создает новое соединение с SQLite."""

    return sqlite3.connect('db.sqlite')


def start_conversation(update, context):
    """Начинает разговор с пользователем и предлагает выбрать мероприятие."""

    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['Свадьба',
          'День рождения',
          'Корпоратив',
          'Выпускной',
          'Поздравление Деда мороза']],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=(
            'Здравствуйте, {}! Пожалуйста, выберите мероприятие, '
            'которое хотите организовать:'
        ).format(name),
        reply_markup=button
    )
    # Устанавливаем состояние на первый вопрос
    conversation_state[chat.id] = 'question1'
    # Инициализируем пустой список для ответов пользователей
    user_responses[chat.id] = []


def ask_question2(update, context):
    """Запрашивает у пользователя количество людей."""

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Количество людей?',
        reply_markup=ReplyKeyboardRemove()
    )
    conversation_state[chat.id] = 'question2'


def ask_question3(update, context):
    """Запрашивает у пользователя желаемую дату."""

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Желаемая дата?',
        reply_markup=ReplyKeyboardRemove()
    )
    conversation_state[chat.id] = 'question3'


def ask_question4(update, context):
    """Запрашивает у пользователя место проведения мероприятия."""

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Место проведения?',
        reply_markup=ReplyKeyboardRemove()
    )
    conversation_state[chat.id] = 'question4'


def ask_question5(update, context):
    """Запрашивает у пользователя имя."""

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Имя?',
        reply_markup=ReplyKeyboardRemove()
    )
    conversation_state[chat.id] = 'question5'


def ask_question6(update, context):
    """Запрашивает у пользователя номер телефона."""

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Номер телефона?',
        reply_markup=ReplyKeyboardRemove()
    )
    conversation_state[chat.id] = 'question6'


def send_survey_results(update, context):
    """Сохраняет результаты опроса в базу данных и отправляет уведомление."""

    chat = update.effective_chat
    # Получаем сохраненные ответы пользователей
    responses = user_responses[chat.id]

    # Сохраняем ответы в базе данных
    with create_connection() as con:
        cur = con.cursor()
        cur.execute(
            """INSERT INTO survey_responses 
            (question1, question2, question3, question4, question5, question6)
            VALUES (?, ?, ?, ?, ?, ?)""",
            responses
        )
        con.commit()

    # Отправляем результаты опроса в ваш личный чат
    context.bot.send_message(
        chat_id=CHAT_ID,
        text='Новая заявка на мероприятие: {}'.format(responses)
    )

    # Отправляем благодарственное сообщение пользователю
    context.bot.send_message(
        chat_id=chat.id,
        text='Спасибо за ответы, в ближайшее время я свяжусь с вами.',
        reply_markup=ReplyKeyboardRemove()
    )


def handle_message(update, context):
    """
    Обрабатывает сообщения от пользователей
    и управляет состоянием разговора.
    """

    chat = update.effective_chat

    # Инициализируем состояние разговора, если оно не установлено
    if chat.id not in conversation_state:
        conversation_state[chat.id] = 'start'
        user_responses[chat.id] = []

    # Обработка состояния разговора
    if conversation_state[chat.id] == 'start':
        start_conversation(update, context)
    elif conversation_state[chat.id] == 'question1':
        user_responses[chat.id].append(update.message.text)
        conversation_state[chat.id] = 'question2'
        ask_question2(update, context)
    elif conversation_state[chat.id] == 'question2':
        user_responses[chat.id].append(update.message.text)
        conversation_state[chat.id] = 'question3'
        ask_question3(update, context)
    elif conversation_state[chat.id] == 'question3':
        user_responses[chat.id].append(update.message.text)
        conversation_state[chat.id] = 'question4'
        ask_question4(update, context)
    elif conversation_state[chat.id] == 'question4':
        user_responses[chat.id].append(update.message.text)
        conversation_state[chat.id] = 'question5'
        ask_question5(update, context)
    elif conversation_state[chat.id] == 'question5':
        user_responses[chat.id].append(update.message.text)
        conversation_state[chat.id] = 'question6'
        ask_question6(update, context)
    elif conversation_state[chat.id] == 'question6':
        user_responses[chat.id].append(update.message.text)
        send_survey_results(update, context)


# Регистрация обработчиков команд и сообщений
updater.dispatcher.add_handler(CommandHandler('start', start_conversation))
updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Запуск опроса и ожидание новых сообщений
updater.start_polling()
updater.idle()
