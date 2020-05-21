def help(update, context):
    text = "Внимание! Все действия происходят для активной команды.\n\n" \
           "/add_question [QUESTION]\n" \
           "Добавить новый вопрос.\n" \
           "Параметр [QUESTION] - текст вопроса\n\n" \
           "/question_list\n" \
           "Список всех вопросов команды.\n\n" \
           "/new_team\nРегистрация новой команды.\n\n" \
           "/set_id [ID]\nРегистрация в существующей " \
           "команде.\n\n" \
           "/answer [Q_NUM] [ANS]\nОтправить ответ на " \
           "вопрос.\nПараметр [Q_NUM] - номер вопроса.\n" \
           "Параметр [ANS] - " \
           "текст с ответом.\n\n" \
           "/set_standups\nНазначить расписание стендапов\n" \
           "(формат записи запроса: [DAY] [TIME] [PERIOD], " \
           "где [DAY] должен быть записан как SUNDAY, " \
           "MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY или " \
           "SATURDAY, [TIME] записывается в формате [HOURS]:" \
           "[MINUTES] (например, 9:23, но не 09:23), " \
           "[PERIOD] - количество недель между стендапами в " \
           "данный день недели.\n\n" \
           "/set_name [NAME]\nИзменить название активной " \
           "команды.\n\n" \
           "/set_active_team\nВыбрать активную команду.\n\n" \
           "/show_standups [NUM]\nВывести последние стендапы.\nПараметр [NUM] задает их количество.\n" \
           "Без параметров - весь список\n\n" \
           "/standup_info [S_NUM]\nВывести информацию о стендапе (дата, вопросы, ответы участников).\n" \
           "Параметр [S_NUM] - номер стендапа.\n\n" \
           "/remove_question\nУдалить вопрос активной команды.\n\n" \
           "/remove_team\nУдалить команду.\n\n" \
           "/leave_team\nПокинуть команду.\n\n" \
           "/join_connect_chats\nПолучать результаты стендапов команды.\n\n" \
           "/leave_connect_chats\nПрекратить получать результаты стендапов команды.\n\n" \
           "/timezone [+-hh:mm]\nУстановить таймзону.\nПараметр [hh:mm] -  сдвиг по UTC.\n\n" \
           "/set_owner\nСмена владельца команды.\n\n" \
           "/send_delta [hh:mm]\n" \
           "Установить время через которое приходят результаты стендапа.\n\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
