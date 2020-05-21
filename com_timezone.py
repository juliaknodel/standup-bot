from team import get_team_db_id
from team import db_teams
from user_input import is_integer_number
from exception import BotUserException


def set_timezone(update, context):
    try:
        nec_args_numb = 2
        timezone = ''.join(list(context.args))
        timezone = timezone.split(':')
        if len(timezone) != nec_args_numb:
            raise BotUserException("Неверный формат ввода часового пояса.\n")
        new_timezone = get_timezone_db_format(hour=timezone[0], minute=timezone[1])

        team_db_id, err_message = get_team_db_id(update.effective_chat.id)
        if team_db_id is False:
            raise BotUserException(err_message)
        db_teams.update_one({"_id": team_db_id}, {"$set": {"timezone": new_timezone}})
        context.bot.send_message(chat_id=update.effective_chat.id, text="Часовой пояс обновлен.\n")
    except BotUserException as bue:
        context.bot.send_message(chat_id=update.effective_chat.id, text=bue.message)


def get_timezone_db_format(hour, minute):
    if not is_integer_number(hour) or not is_integer_number(minute):
        raise BotUserException("Неверный формат ввода часового пояса.\n")

    hour, minute = int(hour), int(minute)
    if (abs(hour) <= 11 and 0 <= minute <= 59) or (abs(hour) == 12 and minute == 0):
        if hour > 0:
            return str(-hour) + " " + str(-minute)
        else:
            return str(-hour) + " " + str(minute)
    else:
        raise BotUserException("Неверный формат ввода часового пояса.\n")
