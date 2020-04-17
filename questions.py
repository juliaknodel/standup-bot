import os
from team import get_team_id
from team import collection
from team import existing_user


db_teams = collection.teams
db_standups = collection.standups


def add_question(update, context):
    db_questions = collection.questions
    db_teams = collection.teams
    user_chat_id = update.effective_chat.id
    team_db_id = get_team_db_id(user_chat_id)

    # здесь будет проверка на права доступа к добавлению вопроса и
    # соответствующее сообщение при ошибке доступа

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text="Номер команды введен некорректно. "
                                                            "Либо вы не состоите в команде.")
    else:
        if not context.args:
            context.bot.send_message(chat_id=user_chat_id, text="Пожалуйста, добавьте текст вопроса"
                                                                " после команды.")
        else:
            text = ' '.join(list(context.args))
            # пока команда одна => вопросы добавляем без вопроса в какую команду
            question = get_new_question_document(text)
            question_db_id = db_questions.insert_one(question).inserted_id
            db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'questions': question_db_id}})
            context.bot.send_message(chat_id=user_chat_id, text="Был добавлен вопрос: " +
                                                                text)


def show_questions_list(update, context):
    user_chat_id = update.effective_chat.id
    team_db_id = get_team_db_id(user_chat_id)

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    questions = get_team_questions_list(team_db_id)
    if len(questions) == 0:
        context.bot.send_message(chat_id=user_chat_id, text='Список вопросов пока пуст.')
    else:
        text = '- ' + '\n- '.join(questions)
        context.bot.send_message(chat_id=user_chat_id, text=text)


def get_new_question_document(text):
    question = {'question': text}

    return question


def get_team_db_id(user_chat_id, team_number=0):
    # team_number - понадобится в будущем для выбора команды из списка
    teams = collection.users.find_one({'chat_id': user_chat_id})['teams']
    if len(teams) > team_number > -1:
        return teams[team_number]
    else:
        return False


def get_team_questions_list(team_db_id):
    questions_id = collection.teams.find_one({'_id': team_db_id})['questions']
    questions = []
    for q_id in questions_id:
        question = collection.questions.find_one({'_id': q_id})['question']
        questions.append(question)
    return questions


def set_standups(update, context):
    args = context.args
    err_message = check_standups_input(args)
    if err_message is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=err_message)
        return
    # TODO: добавить проверку, в какую команду назначается расписание стендапов, если команд несколько
    # TODO: добавить проверку, является ли пользователь администратором в команде
    team_db_id = get_team_db_id(update.effective_chat.id)
    write_schedule_to_db(context.args, team_db_id)
    create_first_standup(team_db_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Расписание стендапов обновлено.")


# TODO: упростить формат ввода дней (сопоставить дням натуральные числа от 1 до 7, прописать соответствие в /help)
ALL_DAYS = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
def check_standups_input(args):
    args_number = len(args)
    standup_days = []
    if args_number == 0 or args_number % 3 != 0:
        return "Введено недостаточное количество входных данных."
    for arg_ind in range(0, args_number, 3):
        day_ind = arg_ind
        time_ind = arg_ind + 1
        period_ind = arg_ind + 2

        if args[day_ind] not in ALL_DAYS:
            return args[day_ind] + " - недопустимое значение дня недели."
        if args[day_ind] in standup_days:
            return "День " + args[day_ind] +" введен дважды. Это недопустимо.."
        else:
            standup_days.append(args[day_ind])

        if is_time_value(args[time_ind]) is False:
            return args[time_ind] + " - недопустимое значение времени."

        if is_natural_number(args[period_ind]) is False:
            return args[period_ind] + " - недопустимое значение периода стендапа."


def create_first_standup(team_db_id):
    # TODO: реализовать вычисление ближайшиего дня и заменить "пустые" аргументы вычисленными
    standup = get_new_standup_document([], {}, "", "")
    standup_db_id = db_standups.insert_one(standup).inserted_id
    standups_db_id = [standup_db_id]
    db_teams.update_one({"_id": team_db_id}, {"$addToSet": {'standups': standups_db_id}})


def get_new_standup_document(questions, answers, date, time):
    standup = {'questions': questions,
               'answers': answers,
               'date': date,
               'time': time}
    return standup


def write_schedule_to_db(args, team_db_id):
    args_number = len(args)
    schedule = []
    for arg_ind in range(0, args_number, 3):
        day_ind = arg_ind
        time_ind = arg_ind + 1
        period_ind = arg_ind + 2
        schedule.append({"day": args[day_ind], "time": args[time_ind], "period": args[period_ind]})
    collection.teams.update_one({"_id": team_db_id}, {"$set": {"schedule": schedule}})


def is_time_value(str):
    time_delimiter = ':'
    try:
        time_delimiter_ind = get_time_delimiter_ind(str, time_delimiter)
        check_hours(str, time_delimiter_ind)
        check_minutes(str, time_delimiter_ind)
        return True
    except ValueError:
        return False


def get_time_delimiter_ind(time, time_delimiter):
    ind = 0
    while ind < len(time):
        if ind == len(time) - 1:
            raise ValueError
        if time[ind] == time_delimiter:
            return ind
        ind += 1


def check_hours(time, time_delimiter_ind):
    hours = time[0:time_delimiter_ind]
    if int(hours) < 0 or int(hours) >= 24:
        raise ValueError


def check_minutes(time, time_delimiter_ind):
    minutes = time[time_delimiter_ind + 1:len(time)]
    if int(minutes) < 0 or int(minutes) >= 60:
        raise ValueError


def is_integer_number(str):
    try:
        number = int(str)
        return True
    except ValueError:
        return False


def is_natural_number(str):
    try:
        number = int(str)
        if number <= 0:
            return False
        else:
            return True
    except ValueError:
        return False


# TODO: реализовать функцию отправки ответа
def answer(update, context):
    if is_possible_to_ans() is False:
        return

# TODO: реализовать функцию проверки возможности отправить ответ
def is_possible_to_ans():
    return False
