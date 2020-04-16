import os
from team import get_team_id


def add_question(update, context):
    chat_id = update.effective_chat.id
    team_id = get_team_id(update)
    if team_id is "":
        context.bot.send_message(chat_id=chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                       "или введите id вашей команды (/set_id [id])")
    else:
        file_name = team_id + '_questions.txt'
        if not context.args:
            context.bot.send_message(chat_id=chat_id, text="Пожалуйста, добавьте текст вопроса"
                                                           " после команды.")
        else:
            with open(file_name, 'a') as f:
                question = list(context.args)
                f.write(' '.join(question) + '\n')
                context.bot.send_message(chat_id=chat_id, text="Был добавлен вопрос: " +
                                                               ' '.join(question))


def show_questions_list(update, context):
    chat_id = update.effective_chat.id
    team_id = get_team_id(update)
    if team_id is "":
        context.bot.send_message(chat_id=chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                       "или введите id вашей команды (/set_id [id])")
    else:
        text = ''
        # file_name = str(update.effective_user.id) + 'questions.txt'
        file_name = team_id + '_questions.txt'
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            with open(file_name, 'r') as f:
                for line in f:
                    text += '- ' + line
                context.bot.send_message(chat_id=chat_id, text=text)
        else:
            context.bot.send_message(chat_id=chat_id, text='Список вопросов пока пуст.')


def set_standups(update, context):
    args = context.args
    args_number = len(args)
    err_message = check_standups_input(args)
    if err_message is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=err_message)
        return
    # TODO: write standups to database
    context.bot.send_message(chat_id=update.effective_chat.id, text="Расписание стендапов обновлено.")


ALL_DAYS = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
def check_standups_input(args):
    args_number = len(args)
    standup_days = []
    if args_number % 3 != 0:
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
