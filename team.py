import os


def new_team(update, context):
    chat_id = update.effective_chat.id
    team_id = str(update.effective_user.id) + '_team'  # создание id команды
    user_file_name = str(update.effective_user.id) + '_user.txt'  # такой файл соответствует каждому пользователю

    if os.path.isfile(user_file_name):
        context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в команде.\n"
                                                       "На данный момент вы можете быть участником "
                                                       "только одной команды")
        return

    # в этом файле хранятся вопросы
    with open(team_id + '_questions.txt', 'w'):
        pass

    # в этом файле хранятся id участников
    with open(team_id + '_members.txt', 'w') as f:
        f.write('MEMBER_ID: ' + str(chat_id) + '\n')

    # каждому юзеру соответствует такой файл, в нем хранится id команды
    with open(user_file_name, 'w') as f:
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
        team_id = context.args[0]
        user_file_name = str(chat_id) + '_user.txt'
        members_file_name = team_id + '_members.txt'

        if member_already_in_team(members_file_name, chat_id):
            context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в этой команде.")
        elif os.path.isfile(user_file_name):
            context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в команде.\n"
                                                           "На данный момент вы можете быть участником "
                                                           "только одной команды")
        else:
            with open(user_file_name, 'w') as f:
                f.write('TEAM_ID: ' + team_id)

            with open(members_file_name, 'a') as f:
                f.write('MEMBER_ID: ' + str(chat_id) + '\n')
                context.bot.send_message(chat_id=chat_id, text="Теперь вы в команде!")


def get_team_id(update):
    user_file_name = str(update.effective_user.id) + '_user.txt'

    if os.path.isfile(user_file_name):

        with open(user_file_name, 'r') as f:
            line = f.read()
            ID = line.split(' ')[1]
        return ID
    else:
        return ""


def member_already_in_team(file_name, member_id):
    with open(file_name, 'r') as f:
        for line in f:
            if line == 'MEMBER_ID: ' + str(member_id) + '\n':
                return True
    return False
