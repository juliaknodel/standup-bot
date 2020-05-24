from exception import BotUserException
from standups import get_team_db_id
from settings import collection

db_teams = collection.teams
db_standups = collection.standups


def get_active_team_standup_ids(user_chat_id):
    team_db_id, err_message = get_team_db_id(user_chat_id)
    # TODO: если get_team_db_id в предыдущей строке все-таки будет бросать исключение,
    #  то следующие две строчки можно убрать
    if team_db_id is False:
        raise BotUserException(err_message)
    return db_teams.find_one({'_id': team_db_id})['standups']


def get_standup_date_str(standup_doc, date_delimiter="."):
    day = str(standup_doc['date']['day'])
    month = str(standup_doc['date']['month'])
    year = str(standup_doc['date']['year'])
    return day + date_delimiter + month + date_delimiter + year
