from collections import defaultdict

from team import collection
from team import get_team_connect_chats


# функция, которая ставится как выполняемая задача в JobQueue при оназначении отправки стендапа
# время обговаривается там же - при создании работы,
# тут сразу происходит отправка, те время уже наступило
# team_db_id - передается уже как ObjectId
def send_standup_to_connect_chats(team_db_id, standup_db_id, context):
    # TODO сделать проверку на пришедший тип: является ли ObjectId
    connect_chats = get_team_connect_chats(team_db_id)
    answers = get_standup_answers(standup_db_id)
    merged_standup = ''

    for member_id in answers:
        member_answers = answers[member_id]
        member_answers_text = ''

        for answer in member_answers:
            member_answers_text += str(answer[0]) + '. ' + answer[1] + '\n'

        merged_standup += 'answers by ' + str(member_id) + '\n' + member_answers_text

    if merged_standup == '':
        merged_standup = 'К сожалению, пока ни один из участников не ответил на вопросы'

    for chat in connect_chats:
        user_chat_id = collection.users.find_one({'_id': chat})
        context.bot.send_message(chat_id=user_chat_id, text=merged_standup)


def get_standup_answers(standup_db_id):
    answers = defaultdict(list)
    standup = collection.standups.find_one({'_id': standup_db_id})['answers']

    for answer in standup:
        member_id = answer['id']
        question_num = answer['question_num']
        answer_text = answer['answer']
        answers[member_id].append([question_num, answer_text])
    return answers
