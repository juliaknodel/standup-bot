import os


def add_question(update, context):
    file_name = str(update.effective_user.id) + 'questions.txt'
    if not context.args:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, добавьте текст вопроса"
                                                                        " после команды.")
    else:
        with open(file_name, 'a') as f:
            question = list(context.args)
            f.write(' '.join(question)+'\n')
            context.bot.send_message(chat_id=update.effective_chat.id, text="Был добавлен вопрос: " +
                                                                            ' '.join(question))


def show_questions_list(update, context):
    text = ''
    file_name = str(update.effective_user.id) + 'questions.txt'

    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        with open(file_name, 'r') as f:
            for line in f:
                text += '- ' + line
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Список вопросов пока пуст.')