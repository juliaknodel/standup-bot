def help(update, context):
    text = "Внимание! Все действия происходят для активной команды.\n\n" \
           "/add_question [QUESTION] - " \
           "добавляет в список вопросов QUESTION.\n\n" \
           "/question_list - " \
           "возвращает список всех вопросов для команды.\n\n" \
           "/new_team - регистрация новой команды.\n\n" \
           "/set_id [ID] - регистрация в существующей " \
           "команде.\n\n" \
           "/answer [Q_NUM] [ANS] - отправка ответа на " \
           "вопрос, где [Q_NUM] - номер вопроса, [ANS] - " \
           "текст с ответом.\n\n" \
           "/set_standups - назначение расписания стендапов " \
           "(формат записи запроса: [DAY] [TIME] [PERIOD], " \
           "где [DAY] должен быть записан как SUNDAY, " \
           "MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY или " \
           "SATURDAY, [TIME] записывается в формате [HOURS]:" \
           "[MINUTES] (например, 9:23, но не 09:23), " \
           "[PERIOD] - количество недель между стендапами в " \
           "данный день недели.\n\n" \
           "/set_name [NAME] - изменение названия активной " \
           "команды.\n\n" \
           "/set_active_team - выбор активной команды.\n\n" \
           "/show_standups [NUM] - вывести последние стендапы. Параметр [NUM] задает их количество.\n\n" \
           "/standup_info [S_NUM] - вывести информацию о стендапе (дата, вопросы, ответы участников). " \
           "Команда ожидает на вход номер вопроса [S_NUM].\n\n" \
           "/remove_question - удаление вопроса активной команды\n\n" \
           "/remove_team - удаление команды\n\n" \
           "/leave_team - выход из команды\n\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
