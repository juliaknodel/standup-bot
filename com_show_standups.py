from exception import BotUserException
from user_input import is_natural_number
from query import db_standups
from query import get_active_team_standup_ids
from query import get_standup_date_str


def show_standups(update, context):
    user_chat_id = update.effective_chat.id
    try:
        if len(context.args) != 1:
            raise BotUserException("На вход ожидается один аргумент: число стендапов.\n")
        if not is_natural_number(context.args[0]):
            raise BotUserException(context.args[0] + " - недопустимое значение числа стендапов.\n")
        st_ids = get_active_team_standup_ids(user_chat_id)
        if len(st_ids) == 0:
            raise BotUserException("История стендапов пуста.\n")

        bot_answer_text = ""
        for st_ind in range(-1, max(-len(st_ids), -int(context.args[0])) - 1, -1):
            st_doc = db_standups.find_one({'_id': st_ids[st_ind]})
            st_date = get_standup_date_str(st_doc)
            st_num = len(st_ids) + (st_ind + 1)
            bot_answer_text += "Стендап # " + str(st_num) + ":     " + st_date + "\n"

        context.bot.send_message(chat_id=user_chat_id, text=bot_answer_text)
    except BotUserException as bue:
        context.bot.send_message(chat_id=user_chat_id, text=bue.message)
    # TODO: добавить дополнительный блок except с проверкой на BaseException, в котором:
    #  1. вывести пользователю уведомления о системной ошибке,
    #  2. вывести traceback в консоль устройства, на котором запущен бот, чтобы разработчик знал, где искать ошибку
