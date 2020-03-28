import os


def new_team(update, context):
    chat_id = update.effective_chat.id
    team_id = str(update.effective_user.id) + '_team'  # создание id команды
    user_file_name = str(update.effective_user.id) + '_user.txt'  # такой файл соответствует каждому пользователю

    with open(team_id + '_questions.txt', 'w'):
        pass
    with open(user_file_name, 'w') as f:  # каждому юзеру соответствует такой файл
        f.write('TEAM_ID: ' + team_id)
    context.bot.send_message(chat_id=chat_id, text="ID вашей команды: " + team_id +
                                                   "\nОстальные члены команды должны использовать его "
                                                   "при регистрации.")


def set_id(update, context):
    chat_id = update.effective_chat.id

    if not context.args:
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, после команды введите id или "
                                                       "зарегистрируйте новую команду")
    elif not os.path.isfile(str(context.args[0]) + '_questions.txt'):
        context.bot.send_message(chat_id=chat_id, text="Не существует команды с таким id")
    else:
        user_file_name = str(chat_id) + '_user.txt'

        with open(user_file_name, 'w') as f:  # каждому юзеру соответствует такой файл
            f.write('TEAM_ID: ' + context.args[0])

        context.bot.send_message(chat_id=chat_id, text="Теперь вы в команде!")


def get_id(update):
    user_file_name = str(update.effective_user.id) + '_user.txt'

    if os.path.isfile(user_file_name):

        with open(user_file_name, 'r') as f:  # каждому юзеру соответствует такой файл
            line = f.read()
            ID = line.split(' ')[1]
        return ID
    else:
        return ""
