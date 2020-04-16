import os
from team import get_team_id
from team import collection
from team import existing_user


def add_question(update, context):
    db_questions = collection.questions
    db_teams = collection.teams
    user_chat_id = update.effective_chat.id
    team_db_id = get_team_db_id(user_chat_id)

    # здесь будет проверка на права доступа к добавлению вопроса и
    # соответствующее сообщение при ошибке доступа

    if not existing_user(user_chat_id):
        context.bot.send_message(chat_id=user_chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                            "или введите id вашей команды (/set_id [id])")
        return

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
    if len(questions) == 0:
        context.bot.send_message(chat_id=user_chat_id, text='Список вопросов пока пуст.')
    else:
        text = '- ' + '\n- '.join(questions)
        context.bot.send_message(chat_id=user_chat_id, text=text)


DAYS = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]


def set_standups(update, context):
    args = context.args
    args_number = len(args)
    file_name = get_team_id(update) + "_standups.txt"
    with open(file_name, 'w') as f:
        if args_number % 2 != 0:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Недостаточное количество входных данных.")
            return
        for arg_ind in range(0, args_number - 1, 2):
            if args[arg_ind] not in DAYS:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Проверьте написание дней недели "
                                              "на соответствие формату.")
                return
            f.write(args[arg_ind] + ' ' + args[arg_ind + 1] + '\n')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Расписание стендапов обновлено.")


def get_new_question_document(text):
    question = {'question': text}

    return question


def get_team_db_id(user_chat_id, team_number=0):
    # team_number - понадобится в будущем для выбора команды из списка
    teams = collection.users.find_one({'chat_id': user_chat_id})['teams']
    if len(teams) > team_number > -1:
        return teams[team_number]
    else:
        return False


def get_team_questions_list(team_db_id):
    questions_id = collection.teams.find_one({'_id': team_db_id})['questions']
    questions = []
    for q_id in questions_id:
        question = collection.questions.find_one({'_id': q_id})['question']
        questions.append(question)
    return questions
