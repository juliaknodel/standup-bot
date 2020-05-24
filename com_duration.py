from exception import BotUserException
from user_input import is_integer_number
from team import is_owner
from team import get_team_db_id
from team import db_teams


def com_duration(update, context):
    try:
        user_chat_id = update.effective_chat.id
        team_db_id, err_message = get_team_db_id(user_chat_id)
        if team_db_id is False:
            raise BotUserException(err_message)
        if not is_owner(team_db_id, user_chat_id=user_chat_id):
            raise BotUserException("Данное действие доступно только владельцу команды.\n")

        nec_args_numb = 2
        duration = ''.join(list(context.args))
        duration = duration.split(':')
        if len(duration) != nec_args_numb:
            raise BotUserException("Должно быть передано " + str(nec_args_numb) + " аргумента.\n")

        new_duration = get_duration_db_format(hour=duration[0], minute=duration[1])
        db_teams.update_one({"_id": team_db_id}, {"$set": {"duration": new_duration}})

        context.bot.send_message(chat_id=user_chat_id, text="Продолжительность стендапов обновлена.\n")
    except BotUserException as bue:
        context.bot.send_message(chat_id=update.effective_chat.id, text=bue.message)


def get_duration_db_format(hour, minute):
    if not is_integer_number(hour) or not is_integer_number(minute):
        raise BotUserException("Неверный формат ввода продолжительности.\n")

    hour, minute = int(hour), int(minute)
    if (0 <= hour <= 23 and 0 <= minute <= 59) or (hour == 24 and minute == 0):
        return str(hour) + " " + str(minute)
    else:
        raise BotUserException("Неверный формат ввода продолжительности.\n")
