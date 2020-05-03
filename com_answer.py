from exception import BotUserException
from query import db_teams
from user_input import is_natural_number
from settings import collection
from team import get_team_db_id


def answer(update, context):
    try:
        write_answer_to_db(update, context)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш ответ добавлен.")
    except BotUserException as bue:
        context.bot.send_message(chat_id=update.effective_chat.id, text=bue.message)
    # TODO: добавить дополнительный блок except с проверкой на BaseException, в котором:
    #  1. вывести пользователю уведомления о системной ошибке,
    #  2. вывести traceback в консоль устройства, на котором запущен бот, чтобы разработчик знал, где искать ошибку


def write_answer_to_db(update, context):
    min_args_number = 2
    if len(context.args) < min_args_number:
        raise BotUserException("Недостаточно аргументов.\n")
    q_num, q_ans = get_answer_command_args(context.args)
    team_db_id, err_message = get_team_db_id(update.effective_chat.id)
    # TODO: если get_team_db_id в предыдущей строке все-таки будет бросать исключение,
    #  то следующие две строчки можно убрать
    if not team_db_id:
        raise BotUserException(err_message)
    team = db_teams.find_one({'_id': team_db_id})
    questions = team['questions']
    st_ids = team['standups']
    if len(st_ids) == 0:
        raise BotUserException("В вашей команде пока не проводились стендапы.")
    if q_num > len(questions):
        raise BotUserException("Вопроса с номером " + str(q_num) + " нет.")
    st_id = st_ids[-1]
    collection.standups.update_one({"_id": st_id}, {"$addToSet": {"answers": {"id": update.effective_chat.id,
                                                                              "question_num": q_num,
                                                                              "answer": q_ans}}})


def get_answer_command_args(args):
    if not is_natural_number(args[0]):
        raise BotUserException(args[0] + " - недопустимое значение номера вопроса.")
    q_number = int(args[0])
    q_answer = " ".join(list(args[1:len(args)]))
    return q_number, q_answer
