import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler

from questions import *
from team import *

TOKEN = "TOKEN"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я Стендап бот. \n"
                                                                    "Если ваша команда уже зарегистрирована, "
                                                                    "то введите /set_id <id>.\n"
                                                                    "Чтобы зарегистрировать команду, введите "
                                                                    "/new_team.\n"                                                  
                                                                    "Чтобы узнать что я могу, вызовите команду /help.")


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/add_question [QUESTION] - "
                                                                    "добавляет в список вопросов QUESTION\n"
                                                                    "/question_list - "
                                                                    "возвращает список всех вопросов для команды\n"
                                                                    "/new_team - регистрация новой команды\n"
                                                                    "/set_id [ID] - регистрация в существующей команде")



bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

# добавление вопроса
question_handler = CommandHandler('add_question', add_question)
dispatcher.add_handler(question_handler)

# список вопросов
question_list_handler = CommandHandler('question_list', show_questions_list)
dispatcher.add_handler(question_list_handler)

# регистрация новой команды - возвращает id
new_team_handler = CommandHandler('new_team', new_team)
dispatcher.add_handler(new_team_handler)

# участник сам себя приписывает к команде используя id команды
set_id_handler = CommandHandler('set_id', set_id)
dispatcher.add_handler(set_id_handler)

# назначение дней стендапов
set_standups_handler = CommandHandler('set_standups', set_standups)
dispatcher.add_handler(set_standups_handler)

updater.start_polling()
