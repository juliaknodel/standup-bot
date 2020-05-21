import telegram
from bson import ObjectId
from bson.errors import InvalidId
from telegram import InlineKeyboardMarkup

from settings import collection, jobs, bot
from settings import MAX_NAME_LENGTH


db_users = collection.users
db_teams = collection.teams
db_standups = collection.standups


def new_team(update, context):
    admin_chat_id = update.effective_chat.id
    admin_id = update.effective_user.id

    if not existing_user(admin_chat_id):
        user = get_new_user_document(admin_chat_id)
        # добавили нового юзера в дб
        admin_db_id = db_users.insert_one(user).inserted_id
    else:
        # TODO проверка что участник уже состоит в данной команде
        admin_db_id = get_db_id_by_chat_id(admin_chat_id)
        context.bot.send_message(chat_id=admin_chat_id, text="О, у Вас новая команда!")

    team = get_new_team_document()

    # добавили новую команду в бд
    team_db_id = db_teams.insert_one(team).inserted_id

    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'members': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'connect_chats': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'admins': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$set': {'owner': admin_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$addToSet': {'teams': team_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$set': {'active_team': team_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$set': {'id': admin_id}})

    context.bot.send_message(chat_id=admin_chat_id, text="Новая команда стала активной\n"
                                                         "ID вашей команды: " + str(team_db_id) +
                                                         "\nОстальные члены команды должны использовать его "
                                                         "при регистрации.")


def set_id(update, context):
    user_chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not context.args:
        context.bot.send_message(chat_id=user_chat_id, text="Пожалуйста, после команды введите id или "
                                                            "зарегистрируйте новую команду")

    team_db_id = is_valid_id(context.args[0])
    if not team_db_id or not existing_team(team_db_id):
        context.bot.send_message(chat_id=user_chat_id, text="Не существует команды с таким id")
    else:
        user = existing_user(user_chat_id)
        if not user:
            user = get_new_user_document(user_chat_id)
            # добавили нового юзера в дб
            user_db_id = db_users.insert_one(user).inserted_id
            context.bot.send_message(chat_id=user_chat_id, text="Привет! Это ваша первая команда!")
        else:
            user_teams = user['teams']
            user_db_id = user['_id']
            if team_db_id in user_teams:
                context.bot.send_message(chat_id=user_chat_id, text="Вы уже являетесь участников данной команды.")
                return

        db_users.update_one({'_id': user_db_id}, {'$addToSet': {'teams': team_db_id}})
        db_users.update_one({'_id': user_db_id}, {'$set': {'active_team': team_db_id}})
        db_users.update_one({'_id': user_db_id}, {'$set': {'id': user_id}})
        db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'members': user_db_id}})

        active_team_name = db_teams.find_one({'_id': team_db_id})['name']
        context.bot.send_message(chat_id=user_chat_id, text="ID активной команды: " + str(team_db_id) + '\n\n' +
                                                            "Название активной команды: " + str(active_team_name))


def set_name(update, context):
    # TODO проверка что пользователь является администратором
    user_chat_id = update.effective_chat.id

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    team_db_id, err_message = get_team_db_id(user_chat_id)

    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text=err_message)
        return

    if not context.args:
        context.bot.send_message(chat_id=user_chat_id, text="Пожалуйста, после команды введите новое название команды.")
        return

    team_name = ' '.join(list(context.args))
    if len(team_name) > MAX_NAME_LENGTH:
        context.bot.send_message(chat_id=user_chat_id, text="Количество символов не должно превышать " +
                                                            str(MAX_NAME_LENGTH))
        return

    db_teams.update_one({"_id": team_db_id}, {"$set": {"name": team_name}})
    context.bot.send_message(chat_id=user_chat_id, text="Теперь ваша команда называется " + team_name)


def get_new_team_document():
    team = {'text': [],
            'questions': [],
            'schedule': [],
            'connect_chats': [],
            'owner': [],
            'admins': [],
            'standups': [],
            'name': 'DEFAULT',
            'timezone': "-3 -0"}

    return team


def get_new_user_document(user_chat_id):
    # формат таймзоны неизвестен - потом добавить
    team = {'teams': [],
            'chat_id': user_chat_id}
    return team


def get_db_id_by_chat_id(user_chat_id):
    user = existing_user(user_chat_id)
    if user:
        return user['_id']
    else:
        return False


def existing_user(user_chat_id):
    return collection.users.find_one({'chat_id': user_chat_id})


def existing_team(team_db_id):
    return collection.teams.find_one({'_id': team_db_id})


def is_valid_id(check_id):
    try:
        o_id = ObjectId(check_id)
        return o_id
    except (InvalidId, TypeError):
        return False


def get_team_connect_chats(team_db_id):
    connect_chats = collection.teams.find_one({'_id': team_db_id})['connect_chats']
    return connect_chats


def get_team_db_id(user_chat_id):
    user = collection.users.find_one({'chat_id': user_chat_id})
    if user:
        active_team_db_id, err_message = check_active_team_is_valid(user)
        if active_team_db_id:
            return active_team_db_id, err_message
        return False, err_message
    return False, "Сначала зарегистрируйте команду (/new_team) или введите id вашей команды (/set_id [id])"


def check_active_team_is_valid(user):
    active_team_db_id = user['active_team']
    user_teams = user['teams']
    if active_team_db_id not in user_teams:
        err_message = 'Список ваших команд изменился - выберите новую активную команду'
        return False, err_message
    return active_team_db_id, 'OK'


def com_set_active_team(update, context):
    """Функция, реализующая выбор команды участника для взаимодействия с помощью кнопок"""
    user_chat_id = update.effective_chat.id
    user = existing_user(user_chat_id)
    if not user or not len(user['teams']):
        context.bot.send_message(chat_id=user_chat_id, text="Вы пока не состоите ни в одной команде")
        return

    user_db_id = user['_id']
    key = get_teams_list_inline_keyboard(user_db_id)

    context.bot.send_message(chat_id=user_chat_id, text="Команды: ", reply_markup=key)


def get_teams_list_inline_keyboard(user_db_id, command_text='SET_ACTIVE_TEAM', exit_button=False):
    user_teams_list = db_users.find_one({'_id': user_db_id})['teams']
    teams_names_list = [db_teams.find_one({'_id': team_id})['name'] for team_id in user_teams_list]
    buttons = []
    for team_num in range(len(user_teams_list)):
        team_name = teams_names_list[team_num]
        team_db_id = user_teams_list[team_num]
        add_info = str(team_num)

        if command_text == 'DEL_MEMBER':
            add_info = str(user_db_id)

        send_data = command_text + ' ' + add_info + ' ' + str(team_db_id)
        button = telegram.InlineKeyboardButton(team_name, url=None,
                                               callback_data=send_data,
                                               switch_inline_query=None,
                                               switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                               login_url=None)
        buttons.append(button)

    if exit_button:
        send_data = 'EXIT'
        button = telegram.InlineKeyboardButton('Отмена', url=None,
                                               callback_data=send_data,
                                               switch_inline_query=None,
                                               switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                               login_url=None)
        buttons.append(button)

    key = InlineKeyboardMarkup([[button] for button in buttons])
    return key


def set_active_team(update, context, team_num, team_db_id):
    user_chat_id = update.effective_chat.id

    team_db_id = is_valid_id(team_db_id)
    user_teams = db_users.find_one({'chat_id': user_chat_id})['teams']

    # TODO ? обновление кнопок список команд изменился ?
    if not team_db_id or len(user_teams) <= int(team_num) or user_teams[int(team_num)] != team_db_id:
        message = "Ваш список команд изменился"
        return False, message

    active_team_db_id = user_teams[int(team_num)]
    active_team = db_teams.find_one({'_id': active_team_db_id})
    active_team_name = active_team['name']
    active_team_owner_id = active_team['owner']
    active_team_owner_chat_id = db_users.find_one({'_id': active_team_owner_id})['chat_id']
    active_team_owner_username = get_user_username(active_team_owner_chat_id)

    db_users.update_one({'chat_id': user_chat_id}, {"$set": {"active_team": active_team_db_id}})

    message = "Активная команда:" + '\n\n' + \
              "Название: \n" + str(active_team_name) + '\n\n' + \
              "Владелец: \n" + str(active_team_owner_username) + '\n\n' + \
              "ID: \n" + str(active_team_db_id)
    return True, message


def get_teams_able_to_remove_list_inline_keyboard(user_db_id):
    user_teams_list = db_users.find_one({'_id': user_db_id})['teams']
    teams_names_list = [db_teams.find_one({'_id': team_id})['name'] for team_id in user_teams_list]
    buttons = []
    for team_num in range(len(user_teams_list)):
        team_name = teams_names_list[team_num]
        team_db_id = user_teams_list[team_num]
        # TODO перед добавлением проверяем, что юзер состоит в списке администраторов
        send_data = 'REMOVE_TEAM' + ' ' + str(team_db_id)
        button = telegram.InlineKeyboardButton(team_name, url=None,
                                               callback_data=send_data,
                                               switch_inline_query=None,
                                               switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                               login_url=None)
        buttons.append(button)

    send_data = 'EXIT'
    button = telegram.InlineKeyboardButton('Отмена', url=None,
                                           callback_data=send_data,
                                           switch_inline_query=None,
                                           switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                           login_url=None)
    buttons.append(button)

    key = InlineKeyboardMarkup([[button] for button in buttons])
    return key


def com_remove_team(update, context):
    user_chat_id = update.effective_chat.id
    user = existing_user(user_chat_id)
    if not user or not len(user['teams']):
        context.bot.send_message(chat_id=user_chat_id, text="Вы пока не состоите ни в одной команде")
        return

    user_db_id = user['_id']
    key = get_teams_able_to_remove_list_inline_keyboard(user_db_id)

    context.bot.send_message(chat_id=user_chat_id, text="Команды доступные для удаления: ", reply_markup=key)


def remove_team(team_db_id):

    team_db_id = is_valid_id(team_db_id)
    if not team_db_id:
        message = "Ваш список команд изменился"
        return False, message

    team = db_teams.find_one({'_id': team_db_id})
    if not team:
        message = "Такая команда не существует"
        return False, message

    name = team['name']
    members = team['members']
    standups = team['standups']

    old_jobs = jobs[team_db_id]
    for weekday_jobs in old_jobs:
        for job in weekday_jobs:
            job.schedule_removal()  # остановили работу по отправке вопросов и ответов

    for member_db_id in members:
        db_users.update_one({'_id': member_db_id}, {'$pull': {'teams': team_db_id}})

    for standup_db_id in standups:
        db_standups.remove({'_id': standup_db_id})

    db_teams.remove({'_id': team_db_id})

    message = 'Команда ' + name + ' успешно удалена.'
    return True, message


def com_leave_team(update, context):
    user_chat_id = update.effective_chat.id
    user = existing_user(user_chat_id)
    if not user or not len(user['teams']):
        context.bot.send_message(chat_id=user_chat_id, text="Вы пока не состоите ни в одной команде")
        return

    user_db_id = user['_id']
    key = get_teams_list_inline_keyboard(user_db_id, command_text='DEL_MEMBER', exit_button=True)

    context.bot.send_message(chat_id=user_chat_id, text="Ваши команды: ", reply_markup=key)


def remove_team_member(team_db_id, user_db_id):

    team_db_id = is_valid_id(team_db_id)
    team = db_teams.find_one({'_id': team_db_id})
    if not team:
        message = "Такая команда не существует"
        return False, message

    user_db_id = is_valid_id(user_db_id)
    user = db_users.find_one({'_id': user_db_id})
    if not user or not len(user['teams']):
        message = "Вы пока не состоите ни в одной команде"
        return False, message

    if team['owner'] == user_db_id:
        message = "Вы владелец команды. Пожалуйста, сначала передайте права на управление другому участнику."
        return False, message

    if len(team['members']) == 1:
        message = "Вы последний участник команды. Пожалуйста, воспользуйтесь командой /remove_team, чтобы удалить её."
        return False, message

    # TODO проверка что администратор (тк могли удалить, а кнопка нажмется позднее, чем была вызвана)
    #  message return иначе
    #  если я супер-администратор - message: переназначить (кнопки) and return

    db_teams.update_one({'_id': team_db_id}, {'$pull': {'connect_chats': user_db_id}})
    db_teams.update_one({"_id": team_db_id}, {'$pull': {'members': user_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$pull': {'admins': user_db_id}})
    db_users.update_one({'_id': user_db_id}, {'$pull': {'teams': team_db_id}})

    team_name = team['name']
    message = 'Вы вышли из команды ' + team_name + '.\n'
    if user['active_team'] == team_db_id:
        message = '\nВы вышли из активной команды. Выберите новую активную команду: /set_active_team'
    return True, message


def com_join_connect_chats(update, context):
    user_chat_id = update.effective_chat.id
    user = existing_user(user_chat_id)
    if not user or not len(user['teams']):
        context.bot.send_message(chat_id=user_chat_id, text="Вы пока не состоите ни в одной команде.")
        return

    team_db_id, err_message = get_team_db_id(user_chat_id)
    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text=err_message)
        return

    team_name = db_teams.find_one({'_id': team_db_id})['name']
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'connect_chats': user['_id']}})

    context.bot.send_message(chat_id=user_chat_id, text='Теперь вы будете получать результаты стендапов команды ' +
                             team_name)


def get_user_username(chat_id):

    user_id = db_users.find_one({'chat_id': chat_id})['id']

    if str(chat_id)[0] == '-':
        chat = bot.getChat(chat_id)
        username = chat.username
        if not username:
            username = chat.title
    else:
        chat_member = bot.getChatMember(chat_id, user_id)
        user = chat_member.user
        username = user.username
        if not username:
            username = user.full_name
    return username
