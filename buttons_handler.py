from questions import delete_question
from team import set_active_team, remove_team_member
from team import remove_team
from settings import collection
from bson import ObjectId
db_standups = collection.standups


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

    elif data[0] == "SHOW_STANDUPS":
        status, message = True, generate_standup_info_text(st_id=data[1], st_number=data[2])

    query.edit_message_text(text=message)


def generate_standup_info_text(st_id, st_number):
    st_doc = db_standups.find_one({'_id': ObjectId(st_id)})
    st_date = get_standup_date_str(st_doc)
    st_questions = st_doc['questions']
    st_answers = st_doc['answers']

    info_text = "Стендап # " + str(st_number) + " от " + st_date + ".\n"
    info_text += "\n"

    info_text += "Вопросы.\n"
    for ind in range(len(st_questions)):
        info_text += str(ind + 1) + ". " + st_questions[ind] + "\n"
    info_text += "\n"

    info_text += "Ответы.\n"
    if len(st_answers) == 0:
        info_text += "Ни один из участников не давал ответов на вопросы.\n"
    else:
        for st_answer in st_answers:
            q_number = str(st_answer['question_num'])
            q_answer = st_answer['answer']
            author_id = str(st_answer['id'])
            info_text += q_number + ". " + q_answer + " (" + author_id + ")\n"

    return info_text


def get_standup_date_str(standup_doc, date_delimiter="."):
    day = str(standup_doc['date']['day'])
    month = str(standup_doc['date']['month'])
    year = str(standup_doc['date']['year'])
    return day + date_delimiter + month + date_delimiter + year
