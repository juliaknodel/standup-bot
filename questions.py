import os
from team import get_id


def add_question(update, context):
    chat_id = update.effective_chat.id
    team_id = get_id(update)
    if team_id is "":
        context.bot.send_message(chat_id=chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                       "или введите id вашей команды (/set_id [id])")
    else:
        file_name = team_id + '_questions.txt'
        if not context.args:
            context.bot.send_message(chat_id=chat_id, text="Пожалуйста, добавьте текст вопроса"
                                                           " после команды.")
        else:
            with open(file_name, 'a') as f:
                question = list(context.args)
                f.write(' '.join(question) + '\n')
                context.bot.send_message(chat_id=chat_id, text="Был добавлен вопрос: " +
                                                               ' '.join(question))


def show_questions_list(update, context):
    chat_id = update.effective_chat.id
    team_id = get_id(update)
    if team_id is "":
        context.bot.send_message(chat_id=chat_id, text="Сначала зарегистрируйте команду (/new_team) "
                                                       "или введите id вашей команды (/set_id [id])")
    else:
        text = ''
        # file_name = str(update.effective_user.id) + 'questions.txt'
        file_name = team_id + '_questions.txt'
        if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
            with open(file_name, 'r') as f:
                for line in f:
                    text += '- ' + line
                context.bot.send_message(chat_id=chat_id, text=text)
        else:
            context.bot.send_message(chat_id=chat_id, text='Список вопросов пока пуст.')
