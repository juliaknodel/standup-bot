import telegram
from telegram.ext import Updater, CallbackQueryHandler
import logging
from telegram.ext import CommandHandler

from buttons_handler import buttons_handler
from questions import add_question
from questions import show_questions_list
from questions import com_remove_question
from com_start import start
from com_help import help
from standups import set_standups
from com_answer import answer
from com_show_standups import show_standups
from com_standup_info import show_standup_info
from team import new_team, set_id, set_name, com_set_active_team, com_remove_team, com_leave_team, \
    com_join_connect_chats

from secrets import TOKEN

updater = Updater(token=TOKEN, use_context=True)

j = updater.job_queue

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

# отправка ответа на вопросы
set_answer_handler = CommandHandler('answer', answer)
dispatcher.add_handler(set_answer_handler)

# изменение названия команды
set_name_handler = CommandHandler('set_name', set_name)
dispatcher.add_handler(set_name_handler)

# изменение названия команды
set_active_team_handler = CommandHandler('set_active_team', com_set_active_team)
dispatcher.add_handler(set_active_team_handler)

# обработка нажатия на кнопку для выбора активной команды
updater.dispatcher.add_handler(CallbackQueryHandler(buttons_handler))

# вывод списка стендапов
show_standups_handler = CommandHandler('show_standups', show_standups)
dispatcher.add_handler(show_standups_handler)

# вывод информации о стендапе по его номеру
standup_info_handler = CommandHandler('standup_info', show_standup_info)
dispatcher.add_handler(standup_info_handler)

# удаление вопроса
remove_question_handler = CommandHandler('remove_question', com_remove_question)
dispatcher.add_handler(remove_question_handler)

# удаление команды
remove_team_handler = CommandHandler('remove_team', com_remove_team)
dispatcher.add_handler(remove_team_handler)

# выход из команды
leave_team_handler = CommandHandler('leave_team', com_leave_team)
dispatcher.add_handler(leave_team_handler)

# выход из команды
join_connect_chats_handler = CommandHandler('join_connect_chats', com_join_connect_chats)
dispatcher.add_handler(join_connect_chats_handler)

updater.start_polling()
