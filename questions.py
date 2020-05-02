from team import collection
from team import existing_user
from team import get_team_db_id

db_teams = collection.teams
db_standups = collection.standups
db_questions = collection.questions


def add_question(update, context):
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
            team_questions = get_team_questions_list(team_db_id)
            if text in team_questions:
                context.bot.send_message(chat_id=user_chat_id, text="В вашей команде уже есть такой вопрос")
                return
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
        message = ""
        for question_ind in range(len(questions_list)):
            message += str(question_ind + 1) + ". " + questions_list[question_ind] + "\n"
        return message


def get_new_question_document(text):
    question = {'question': text}

    return question


def get_team_questions_list(team_db_id):
    questions_id = collection.teams.find_one({'_id': team_db_id})['questions']
    questions = []
    for q_id in questions_id:
        question = collection.questions.find_one({'_id': q_id})['question']
        questions.append(question)
    return questions
