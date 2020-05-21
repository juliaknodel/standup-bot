from team import get_team_db_id
from settings import collection

db_teams = collection.teams
db_users = collection.users


def com_leave_connect_chats(update, context):
    user_chat_id = update.effective_chat.id
    team_db_id, err_message = get_team_db_id(user_chat_id)
    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text=err_message)
        return
    user_db_id = db_users.find_one({'chat_id': user_chat_id})['_id']
    db_teams.update_one({'_id': team_db_id}, {'$pull': {'connect_chats': user_db_id}})

    team_name = db_teams.find_one({'_id': team_db_id})['name']
    context.bot.send_message(chat_id=user_chat_id, text='Вы больше не будете получать результаты '
                                                        'стендапов команды ' + str(team_name) + '.')
