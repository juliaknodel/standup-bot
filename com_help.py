def help(update, context):
    text = "Все действия происходят для активной команды\n" \
           "/add_question [QUESTION] - " \
           "добавляет в список вопросов QUESTION.\n" \
           "/question_list - " \
           "возвращает список всех вопросов для команды.\n" \
           "/new_team - регистрация новой команды.\n" \
           "/set_id [ID] - регистрация в существующей " \
           "команде.\n" \
           "/answer [Q_NUM] [ANS] - отправка ответа на " \
           "вопрос, где [Q_NUM] - номер вопроса, [ANS] - " \
           "текст с ответом.\n" \
           "/set_standups - назначение расписания стендапов " \
           "(формат записи запроса: [DAY] [TIME] [PERIOD], " \
           "где [DAY] должен быть записан как SUNDAY, " \
           "MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY или " \
           "SATURDAY, [TIME] записывается в формате [HOURS]:" \
           "[MINUTES] (например, 9:23, но не 09:23), " \
           "[PERIOD] - количество недель между стендапами в " \
           "данный день недели.\n" \
           "/set_name [NAME] - изменение названия активной " \
           "команды.\n" \
           "/set_active_team - выбор активной команды.\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
