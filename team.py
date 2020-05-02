import telegram
from bson import ObjectId
from bson.errors import InvalidId
from telegram import InlineKeyboardMarkup

from settings import collection
from settings import MAX_NAME_LENGTH

db_users = collection.users
db_teams = collection.teams


def new_team(update, context):
    admin_chat_id = update.effective_chat.id

    if not existing_user(admin_chat_id):
        user = get_new_user_document(admin_chat_id)
        # добавили нового юзера в дб
        admin_db_id = db_users.insert_one(user).inserted_id
    else:
        # TODO проверка что участник уже состоит в данной команде
        admin_db_id = get_db_id_by_chat_id(admin_chat_id)
        # при снятии заглушки этот код:
        context.bot.send_message(chat_id=admin_chat_id, text="О, у Вас новая команда!")
        # заглушка на мультикомандность
        # context.bot.send_message(chat_id=admin_chat_id, text="Привет! На данный момент вы не можете быть "
        #                                                      "участником более чем одной команды.")
        # return

    team = get_new_team_document()

    # добавили новую команду в бд
    team_db_id = db_teams.insert_one(team).inserted_id

    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'members': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'connect_chats': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'admins': admin_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$addToSet': {'teams': team_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$set': {'active_team': team_db_id}})

    context.bot.send_message(chat_id=admin_chat_id, text="Новая команда стала активной\n"
                                                         "ID вашей команды: " + str(team_db_id) +
                                                         "\nОстальные члены команды должны использовать его "
                                                         "при регистрации.")


def set_id(update, context):
    user_chat_id = update.effective_chat.id

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
            # заглушка на мультикомандность
            # context.bot.send_message(chat_id=user_chat_id, text="На данный момент вы не можете быть "
            #                                                     "участником более чем одной команды.")
            # return
            # при снятии заглушки этот код:
            #
            # проверка что уже состоит в конкретной команде - сообщение об этом
            # иначе
            user_teams = user['teams']
            user_db_id = user['_id']
            if team_db_id in user_teams:
                context.bot.send_message(chat_id=user_chat_id, text="Вы уже являетесь участников данной команды.")
                return

        db_users.update_one({'_id': user_db_id}, {'$addToSet': {'teams': team_db_id}})
        db_users.update_one({'_id': user_db_id}, {'$set': {'active_team': team_db_id}})
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

    team_db_id, err_message = get_team_db_id(user_chat_id, team_number=0)

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
            'admins': [],
            'standups': [],
            'name': 'DEFAULT',
            'timezone': -3}

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


def get_team_db_id(user_chat_id, team_number=0):
    # team_number - понадобится в будущем для выбора команды из списка
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


def set_active_team(update, context):
    """Функция, реализующая выбор команды участника для взаимодействия с помощью кнопок"""
    user_chat_id = update.effective_chat.id
    user_db_id = get_db_id_by_chat_id(user_chat_id)
    key = get_teams_list_inline_keyboard(user_db_id)
    if not user_db_id:
        context.bot.send_message(chat_id=user_chat_id, text="Вы пока не состоите ни в одной команде")
        return

    context.bot.send_message(chat_id=user_chat_id, text="Команды: ", reply_markup=key)


def get_teams_list_inline_keyboard(user_db_id):
    user_teams_list = db_users.find_one({'_id': user_db_id})['teams']
    teams_names_list = [db_teams.find_one({'_id': team_id})['name'] for team_id in user_teams_list]
    buttons = []
    for team_num in range(len(user_teams_list)):
        button = telegram.InlineKeyboardButton(teams_names_list[team_num], url=None,
                                               callback_data=team_num,
                                               switch_inline_query=None,
                                               switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                               login_url=None)
        buttons.append(button)

    key = InlineKeyboardMarkup([[button] for button in buttons])
    return key


def teams(update, context):
    user_chat_id = update.effective_chat.id

    query = update.callback_query
    query.answer()
    team_num = int(query.data)

    user_teams = db_users.find_one({'chat_id': user_chat_id})['teams']
    active_team_db_id = user_teams[int(team_num)]
    active_team_name = db_teams.find_one({'_id': active_team_db_id})['name']

    db_users.update_one({'chat_id': user_chat_id}, {"$set": {"active_team": active_team_db_id}})

    context.bot.send_message(chat_id=user_chat_id, text="ID активной команды: " + str(active_team_db_id) + '\n\n' +
                                                        "Название активной команды: " + str(active_team_name))

