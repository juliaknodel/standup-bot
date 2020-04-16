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


DAYS = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]


def set_standups(update, context):
    args = context.args
    args_number = len(args)
    file_name = get_team_id(update) + "_standups.txt"
    with open(file_name, 'w') as f:
        if args_number % 2 != 0:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Недостаточное количество входных данных.")
            return
        for arg_ind in range(0, args_number - 1, 2):
            if args[arg_ind] not in DAYS:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Проверьте написание дней недели "
                                              "на соответствие формату.")
                return
            f.write(args[arg_ind] + ' ' + args[arg_ind + 1] + '\n')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Расписание стендапов обновлено.")