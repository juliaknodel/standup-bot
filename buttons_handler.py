from questions import delete_question, get_team_questions_list, team_questions_text
from team import set_active_team, is_valid_id


def buttons_handler(update, context):
    user_chat_id = update.effective_chat.id

    query = update.callback_query
    query.answer()
    data = query.data.split(' ')
    if data[0] == 'SET_ACTIVE_TEAM':
        status, message = set_active_team(update, context, team_num=data[1], team_db_id=data[2])
        query.edit_message_text(text=message)
    elif data[0] == 'DEL_Q':
        status, message = delete_question(team_db_id=data[1], question_id=data[2])
        query.edit_message_text(text=message)
