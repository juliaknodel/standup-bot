import os

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['bot-test-database']
collection = db['bot-test-collection']


def new_team(update, context):
    admin_chat_id = update.effective_chat.id

    db_users = collection.users
    db_teams = collection.teams

    if not existing_user(admin_chat_id):
        user = get_new_user_document(admin_chat_id)
        # добавили нового юзера в дб
        admin_db_id = db_users.insert_one(user).inserted_id
    else:
        admin_db_id = get_db_id_by_chat_id(admin_chat_id)
        # при снятии заглушки этот код:
        # context.bot.send_message(chat_id=admin_chat_id, text="О, у Вас новая команда!")
        # заглушка на мультикомандность
        context.bot.send_message(chat_id=admin_chat_id, text="Привет! На данный момент вы не можете быть "
                                                             "участником более чем одной команды.")
        return

    team = get_new_team_document()

    # добавили новую команду в бд
    team_db_id = db_teams.insert_one(team).inserted_id

    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'members': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'connect_chats': admin_db_id}})
    db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'admins': admin_db_id}})
    db_users.update_one({'_id': admin_db_id}, {'$addToSet': {'teams': team_db_id}})

    context.bot.send_message(chat_id=admin_chat_id, text="ID вашей команды: " + str(team_db_id) +
                                                         "\nОстальные члены команды должны использовать его "
                                                         "при регистрации.")

    # if os.path.isfile(user_file_name):
    # context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в команде.\n"
    # "На данный момент вы можете быть участником "
    # "только одной команды")
    # return


def set_id(update, context):
    user_chat_id = update.effective_chat.id

    db_users = collection.users
    db_teams = collection.teams

    if not context.args:
        context.bot.send_message(chat_id=user_chat_id, text="Пожалуйста, после команды введите id или "
                                                            "зарегистрируйте новую команду")

    team_db_id = is_valid_id(context.args[0])
    if not team_db_id or not existing_team(team_db_id):
        context.bot.send_message(chat_id=user_chat_id, text="Не существует команды с таким id")
    else:
        if not existing_user(user_chat_id):
            user = get_new_user_document(user_chat_id)
            # добавили нового юзера в дб
            user_db_id = db_users.insert_one(user).inserted_id
            context.bot.send_message(chat_id=user_chat_id, text="Привет! Это ваша первая команда!")
        else:
            # заглушка на мультикомандность
            context.bot.send_message(chat_id=user_chat_id, text="На данный момент вы не можете быть "
                                                                "участником более чем одной команды.")
            return
            # при снятии заглушки этот код:
            #
            # проверка что уже состоит в конкретной команде - сообщение об этом
            # иначе
            # user_db_id = get_db_id_by_chat_id(user_chat_id)
            # context.bot.send_message(chat_id=user_chat_id, text="Вы теперь участник еще одной команды!")

        db_users.update_one({'_id': user_db_id}, {'$addToSet': {'teams': team_db_id}})
        db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'members': user_db_id}})

    # chat_id = update.effective_chat.id
    #
    # if not context.args:
    # context.bot.send_message(chat_id=chat_id, text="Пожалуйста, после команды введите id или "
    # "зарегистрируйте новую команду")
    # elif not os.path.isfile(str(context.args[0]) + '_questions.txt'):
    # context.bot.send_message(chat_id=chat_id, text="Не существует команды с таким id")
    # else:
    # team_id = context.args[0]
    # user_file_name = str(chat_id) + '_user.txt'
    # members_file_name = team_id + '_members.txt'
    #
    # if member_already_in_team(members_file_name, chat_id):
    # context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в этой команде.")
    # elif os.path.isfile(user_file_name):
    # context.bot.send_message(chat_id=chat_id, text="Вы уже состоите в команде.\n"
    # "На данный момент вы можете быть участником "
    # "только одной команды")
    # else:
    # with open(user_file_name, 'w') as f:
    # f.write('TEAM_ID: ' + team_id)
    #
    # with open(members_file_name, 'a') as f:
    # f.write('MEMBER_ID: ' + str(chat_id) + '\n')
    # context.bot.send_message(chat_id=chat_id, text="Теперь вы в команде!")


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


def get_new_team_document():
    team = {'members': [],
            'questions': [],
            'schedule': [],
            'connect_chats': [],
            'admins': [],
            'standups': [],
            'name': 'DEFAULT'}

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
