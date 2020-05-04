def start(update, context):
    text = "Привет! Я Стендап бот.\n" \
           "Если ваша команда уже зарегистрирована, " \
           "то введите /set_id <id>.\n" \
           "Чтобы зарегистрировать команду, введите " \
           "/new_team.\n" \
           "Чтобы узнать, что я могу, вызовите команду /help."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
