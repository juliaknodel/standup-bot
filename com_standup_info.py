from user_input import is_natural_number
from exception import BotUserException
from query import db_standups
from query import get_active_team_standup_ids
from query import get_standup_date_str


def com_show_standup_info(update, context):
    user_chat_id = update.effective_chat.id
    try:
        parse_standup_info_command_input(context.args)

        st_number = int(context.args[0])
        st_ids = get_active_team_standup_ids(user_chat_id)
        if len(st_ids) == 0:
            raise BotUserException("История стендапов пуста.\n")
        if st_number > len(st_ids):
            raise BotUserException("Стендапа с номером " + str(st_number) + " не найдено.\n")

        standup_info_text = generate_standup_info_text(st_id=st_ids[st_number - 1], st_number=st_number)
        context.bot.send_message(chat_id=user_chat_id, text=standup_info_text)
    except BotUserException as bue:
        context.bot.send_message(chat_id=user_chat_id, text=bue.message)
    # TODO: добавить дополнительный блок except с проверкой на BaseException, в котором:
    #  1. вывести пользователю уведомления о системной ошибке,
    #  2. вывести traceback в консоль устройства, на котором запущен бот, чтобы разработчик знал, где искать ошибку


def parse_standup_info_command_input(com_input_args):
    if len(com_input_args) != 1:
        raise BotUserException("Недопустимое количество аргументов.\n")
    if not is_natural_number(com_input_args[0]):
        raise BotUserException(com_input_args[0] + " - недопустимое значение номера стендапа.")


def generate_standup_info_text(st_id, st_number):
    st_doc = db_standups.find_one({'_id': st_id})
    st_date = get_standup_date_str(st_doc)
    st_questions = st_doc['questions']
    st_answers = st_doc['answers']

    info_text = "Стендап # " + str(st_number) + " от " + st_date + ".\n"
    info_text += "\n"

    info_text += "Вопросы.\n"
    for ind in range(len(st_questions)):
        info_text += str(ind + 1) + ". " + st_questions[ind] + "\n"
    info_text += "\n"

    info_text += "Ответы.\n"
    if len(st_answers) == 0:
        info_text += "Ни один из участников не давал ответов на вопросы.\n"
    else:
        for st_answer in st_answers:
            q_number = str(st_answer['question_num'])
            q_answer = st_answer['answer']
            author_id = str(st_answer['id'])
            info_text += q_number + ". " + q_answer + " (" + author_id + ")\n"

    return info_text
