import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler

from questions import *

TOKEN = "TOKEN"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я стендап бот. \n"
                                                                    "Чтобы узнать что я могу, вызовите команду /help.")


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/add_question [QUESTION] - "
                                                                    "добавляет в список вопросов QUESTION\n"
                                                                    "/question_list - "
                                                                    "возвращает список всех вопросов для команды\n")


def settings(update, context):
    pass


bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

settings_handler = CommandHandler('set_settings', settings)
dispatcher.add_handler(settings_handler)

question_handler = CommandHandler('add_question', add_question)
dispatcher.add_handler(question_handler)

question_list_handler = CommandHandler('question_list', show_questions_list)
dispatcher.add_handler(question_list_handler)

updater.start_polling()
