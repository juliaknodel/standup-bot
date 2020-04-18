import os
from team import get_team_id
from team import collection
from team import existing_user


db_teams = collection.teams
db_standups = collection.standups


def add_question(update, context):
    db_questions = collection.questions
    db_teams = collection.teams
    user_chat_id = update.effective_chat.id

    # здесь будет проверка на права доступа к добавлению вопроса и
    # соответствующее сообщение при ошибке доступа

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    team_db_id = get_team_db_id(user_chat_id)

    if not team_db_id:
        context.bot.send_message(chat_id=user_chat_id, text="Номер команды введен некорректно. "
                                                            "Либо вы не состоите в команде.")
    else:
        if not context.args:
            context.bot.send_message(chat_id=user_chat_id, text="Пожалуйста, добавьте текст вопроса"
                                                                " после команды.")
        else:
            text = ' '.join(list(context.args))
            # пока команда одна => вопросы добавляем без вопроса в какую команду
            question = get_new_question_document(text)
            question_db_id = db_questions.insert_one(question).inserted_id
            db_teams.update_one({'_id': team_db_id}, {'$addToSet': {'questions': question_db_id}})
            context.bot.send_message(chat_id=user_chat_id, text="Был добавлен вопрос: " +
                                                                text)


def show_questions_list(update, context):
    user_chat_id = update.effective_chat.id
    team_db_id = get_team_db_id(user_chat_id)

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

    questions = get_team_questions_list(team_db_id)
    message = team_questions_text(questions)
    context.bot.send_message(chat_id=user_chat_id, text=message)


def team_questions_text(questions_list):
    if len(questions_list) == 0:
        return 'Список вопросов пока пуст.'
    else:
        return '- ' + '\n- '.join(questions_list)


def get_new_question_document(text):
    question = {'question': text}

    return question


def get_team_db_id(user_chat_id, team_number=0):
    # team_number - понадобится в будущем для выбора команды из списка
    user = collection.users.find_one({'chat_id': user_chat_id})
    if user:
        teams = user['teams']
        if len(teams) > team_number > -1:
            return teams[team_number]
    return False


def get_team_questions_list(team_db_id):
    questions_id = collection.teams.find_one({'_id': team_db_id})['questions']
    questions = []
    for q_id in questions_id:
        question = collection.questions.find_one({'_id': q_id})['question']
        questions.append(question)
    return questions



