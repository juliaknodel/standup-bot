import telegram
from telegram import InlineKeyboardMarkup
from settings import collection
from team import get_team_db_id, existing_user, get_user_username, is_valid_id, get_db_id_by_chat_id

db_users = collection.users
db_teams = collection.teams


def com_set_owner(update, context):
    user_chat_id = update.effective_chat.id

    user = existing_user(user_chat_id)
    if not user:
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    team_db_id, err_message = get_team_db_id(user_chat_id)
    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text=err_message)
        return

    team = db_teams.find_one({'_id': team_db_id})

    if team['owner'] != user['_id']:
        context.bot.send_message(chat_id=user_chat_id, text="Сменить владельца может только текущий владелец команды.")
        return

    # TODO сообщение в чат с мемберами + заголовок к какой команде выбираем
    key = get_teams_members_list_inline_keyboard(team_db_id)
    title = "Выберите нового владельца команды: " + team['name'] + '\n\nУчастники команды:'
    context.bot.send_message(chat_id=user_chat_id, text=title, reply_markup=key)


def get_teams_members_list_inline_keyboard(team_db_id):
    team_members_ids = db_teams.find_one({'_id': team_db_id})['members']
    team_members_chats_ids = [db_users.find_one({'_id': user_db_id})['chat_id'] for user_db_id in team_members_ids]
    teams_members_names = [get_user_username(user_chat_id) for user_chat_id in team_members_chats_ids]
    buttons = []

    for user_num in range(len(team_members_ids)):
        user_username = str(teams_members_names[user_num])
        user_db_id = str(team_members_ids[user_num])
        send_data = 'SET_OWNER' + ' ' + str(team_db_id) + ' ' + user_db_id
        button = telegram.InlineKeyboardButton(user_username, url=None,
                                               callback_data=send_data,
                                               switch_inline_query=None,
                                               switch_inline_query_current_chat=None, callback_game=None, pay=None,
                                               login_url=None)
        buttons.append(button)

    key = InlineKeyboardMarkup([[button] for button in buttons])
    return key


def set_owner(update, team_db_id, new_owner_db_id):
    user_chat_id = update.effective_chat.id

    new_owner_db_id = is_valid_id(new_owner_db_id)
    user_db_id = get_db_id_by_chat_id(user_chat_id)

    team_db_id = is_valid_id(team_db_id)

    team = db_teams.find_one({'_id': team_db_id})
    if not team:
        message = 'Такой команды не существует.'
        return False, message

    if not user_db_id or team['owner'] != user_db_id:
        message = 'Вы не являетесь владельцем данной команды.'
        return False, message

    if new_owner_db_id not in team['members']:
        message = 'Выбранный пользователь уже не является участником команды.'
        return False, message

    owner_chat_id = db_users.find_one({'_id': new_owner_db_id})['chat_id']
    owner_username = get_user_username(owner_chat_id)

    db_teams.update_one({'_id': team_db_id}, {'$set': {'owner': new_owner_db_id}})
    message = 'Новый владелец команды ' + str(team['name']) + ': ' + str(owner_username)

    return True, message
