from questions import delete_question
from team import set_active_team, remove_team_member
from team import remove_team


def buttons_handler(update, context):

    query = update.callback_query
    query.answer()
    data = query.data.split(' ')

    message = 'Invalid data'

    if data[0] == 'EXIT':
        message = 'Спасибо, что продолжаете работу!'

    elif data[0] == 'SET_ACTIVE_TEAM':
        status, message = set_active_team(update, context, team_num=data[1], team_db_id=data[2])

    elif data[0] == 'DEL_Q':
        status, message = delete_question(team_db_id=data[1], question_id=data[2])

    elif data[0] == 'DEL_MEMBER':
        status, message = remove_team_member(team_db_id=data[2], user_db_id=data[1])

    elif data[0] == 'REMOVE_TEAM':
        status, message = remove_team(team_db_id=data[1])

    query.edit_message_text(text=message)