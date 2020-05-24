import datetime
from collections import defaultdict
from questions import get_team_db_id
from questions import get_team_questions_list
from questions import team_questions_text
from settings import collection, jobs
from team import get_team_connect_chats, get_user_username, is_valid_id, is_owner
from team import existing_user
from user_input import is_natural_number
from query import db_teams
from query import db_standups

db_questions = collection.questions


def set_standups(update, context):
    chat_id = update.effective_chat.id
    team_db_id, err_message = get_team_db_id(chat_id)

    if not team_db_id:
        context.bot.send_message(chat_id=chat_id, text=err_message)
        return

    if not is_owner(team_db_id, user_chat_id=chat_id):
        context.bot.send_message(chat_id=chat_id, text="Данное действие доступно только владельцу команды.")
        return

    err_message = check_standups_input(chat_id, context.args)
    if err_message is not None:
        context.bot.send_message(chat_id=chat_id, text=err_message)
        return

    team = db_teams.find_one({'_id': team_db_id})
    prev_standups = team['standups']
    db_teams.update_one({'_id': team_db_id}, {'$set': {'last_send_standup': len(prev_standups) - 1}})
    write_schedule_to_db(context.args, team_db_id)

    # остановим старые работы этой команды, если они были
    old_jobs = jobs[team_db_id]
    for weekday_jobs in old_jobs:
        for job in weekday_jobs:
            job.schedule_removal()  # остановили работу по отправке вопросов и ответов
    send_questions_jobs, send_answers_jobs = create_first_standup(team_db_id, context, chat_id, update)

    # вернули список с указателями на созданные работы, теперь они хранятся в словаре
    jobs[team_db_id] = [send_questions_jobs, send_answers_jobs]

    context.bot.send_message(chat_id=update.effective_chat.id, text="Расписание стендапов обновлено.")


def get_standup_dates_from_schedule(schedule):
    # получаем номера дней недели со временем, в которые проводим стендапы по расписанию
    schedule_day_nums_time_period = get_standup_weekday_nums_with_time(schedule)

    # получаем словарь с датами и нужным временем всех ближайших дней недели
    next_week_dates = get_next_week_dates(schedule_day_nums_time_period)

    return get_standup_dates(next_week_dates)


def create_first_standup(team_db_id, context, chat_id, update):
    team = db_teams.find_one({'_id': team_db_id})
    schedule = team['schedule']
    duration = team['duration'].split(' ')
    duration = datetime.timedelta(hours=int(duration[0]), minutes=int(duration[1]))

    # получаем словарь дата: интервал всех ближайших стендапов на каждый из дней недели
    standup_dates = get_standup_dates_from_schedule(schedule)

    send_questions_jobs = []
    send_answers_jobs = []
    time = team['timezone'].split(' ')
    delta = datetime.timedelta(hours=int(time[0]), minutes=int(time[1]))
    for date in standup_dates:
        interval = datetime.timedelta(days=7 * standup_dates[date])
        job = context.job_queue.run_repeating(standup_job,
                                              interval=interval,
                                              first=date + delta,
                                              context=team_db_id)
        send_questions_jobs.append(job)

        send_answers_date = date + duration

        job = context.job_queue.run_repeating(send_answers_job, interval=interval,
                                              first=send_answers_date + delta, context=team_db_id)
        send_answers_jobs.append(job)
    return send_questions_jobs, send_answers_jobs


def standup_job(context):
    team_db_id = context.job.context
    questions = get_team_questions_list(team_db_id)

    new_standup(questions, team_db_id)
    send_questions(context, team_db_id, questions)


def send_answers_job(context):
    team_db_id = context.job.context

    team = db_teams.find_one({'_id': team_db_id})
    last_send_standup = team['last_send_standup']
    db_teams.update_one({'_id': team_db_id}, {'$set': {'last_send_standup': last_send_standup + 1}})

    team = db_teams.find_one({'_id': team_db_id})
    team_standups = team['standups']
    last_send_standup = team['last_send_standup']
    standup_db_id = team_standups[last_send_standup]
    send_standup_to_connect_chats(team_db_id, standup_db_id, context)


# функция, которая ставится как выполняемая задача в JobQueue при оназначении отправки стендапа
# время обговаривается там же - при создании работы,
# тут сразу происходит отправка, те время уже наступило
# team_db_id - передается уже как ObjectId
def send_standup_to_connect_chats(team_db_id, standup_db_id, context):
    # TODO сделать проверку на пришедший тип: является ли ObjectId
    connect_chats = get_team_connect_chats(team_db_id)
    answers = get_standup_answers(standup_db_id)
    standups_ids = db_teams.find_one({'_id': team_db_id})['standups']
    standup_num = len(standups_ids)

    questions = db_standups.find_one({'_id': standup_db_id})['questions']
    questions_text = team_questions_text(questions)
    title = 'Результаты стендапа #' + str(standup_num) + '\n\n'
    title += get_title(team_db_id)
    title += questions_text + '\n'
    merged_standup = ''
    for member_chat_id in answers:
        member_answers = answers[member_chat_id]
        member_answers_text = ''

        member_answers.sort(key=lambda x: x[0])
        for answer in member_answers:
            member_answers_text += str(answer[0]) + '. ' + answer[1] + '\n'

        user_username = get_user_username(member_chat_id)
        merged_standup += 'Ответы от ' + str(user_username) + '\n' + member_answers_text

    if merged_standup == '':
        merged_standup = 'К сожалению, пока ни один из участников не ответил на вопросы'

    for chat in connect_chats:
        user_chat_id = collection.users.find_one({'_id': chat})['chat_id']
        context.bot.send_message(chat_id=user_chat_id, text=title + merged_standup)


# возвращает словарь ключ - id участника, значение - список пар [номер_вопроса, ответ]
# {member_id: [[q_num, answer], [q_num, answer], ...]}
def get_standup_answers(standup_db_id):
    answers = defaultdict(list)
    standup = collection.standups.find_one({'_id': standup_db_id})['answers']

    for answer in standup:
        member_id = answer['id']
        question_num = answer['question_num']
        answer_text = answer['answer']
        answers[member_id].append([question_num, answer_text])
    return answers


ALL_DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def check_standups_input(chat_id, args):
    if existing_user(chat_id) is None:
        return "Необходимо зарегистрироваться хотя бы в одной команде."
    args_number = len(args)
    standup_days = []
    if args_number == 0 or args_number % 3 != 0:
        return "Введено недостаточное количество входных данных."
    for arg_ind in range(0, args_number, 3):
        day_ind = arg_ind
        time_ind = arg_ind + 1
        period_ind = arg_ind + 2

        if args[day_ind].upper() not in ALL_DAYS:
            return args[day_ind] + " - недопустимое значение дня недели."
        if args[day_ind].upper() in standup_days:
            return "День " + args[day_ind] + " введен дважды."
        else:
            standup_days.append(args[day_ind].upper())

        if not is_time_value(args[time_ind]):
            return args[time_ind] + " - недопустимое значение времени."
        if not is_natural_number(args[period_ind]):
            return args[period_ind] + " - недопустимое значение периода стендапа."


def new_standup(questions, team_db_id):
    timezone = db_teams.find_one({'_id': team_db_id})['timezone'].split(' ')
    curr_local_time = datetime.datetime.utcnow() - datetime.timedelta(hours=int(timezone[0]),
                                                                      minutes=int(timezone[1]))
    standup = get_new_standup_document(questions=questions,
                                       answers=[],
                                       date={'day': curr_local_time.day,
                                             'month': curr_local_time.month,
                                             'year': curr_local_time.year
                                             },
                                       time={'hour': curr_local_time.hour,
                                             'minute': curr_local_time.minute
                                             },
                                       team_db_id=team_db_id)
    standup_db_id = db_standups.insert_one(standup).inserted_id
    db_teams.update_one({"_id": team_db_id}, {"$addToSet": {'standups': standup_db_id}})


def get_title(team_db_id):
    team_name = db_teams.find_one({'_id': team_db_id})['name']

    title = 'Название команды:\n' + str(team_name) + '\n\nID:\n' + str(team_db_id) + \
            '\n\n'
    return title


def send_questions(context, team_db_id, questions):
    standups_ids = db_teams.find_one({'_id': team_db_id})['standups']
    standup_num = len(standups_ids)

    title = 'Начало стендапа #' + str(standup_num) + '\n\n'
    text = team_questions_text(questions)
    title += get_title(team_db_id)

    members = db_teams.find_one({'_id': team_db_id})['members']
    for member in members:
        chat_id = collection.users.find_one({'_id': member})['chat_id']
        context.bot.send_message(chat_id=chat_id, text=title + text)


def get_standup_dates_from_db(team_db_id):
    return db_teams.find_one({'_id': team_db_id})['standup_dates']


def get_new_standup_document(questions=[], answers=[], date={}, time={}, team_db_id=''):
    standup = {'questions': questions,
               'answers': answers,
               'date': date,
               'time': time,
               'team_db_id': team_db_id}
    return standup


def write_schedule_to_db(args, team_db_id):
    args_number = len(args)
    schedule = []
    for arg_ind in range(0, args_number, 3):
        day_ind = arg_ind
        time_ind = arg_ind + 1
        period_ind = arg_ind + 2
        hours, mins = get_time(args[time_ind])
        schedule.append({"day": args[day_ind].upper(), "hours": hours, "minutes": mins, "period": args[period_ind]})
    collection.teams.update_one({"_id": team_db_id}, {"$set": {"schedule": schedule}})


def get_time(time_str):
    time = time_str.split(':')
    hours, minutes = time[0], time[1]
    if len(hours) == 2 and hours[0] == '0':   # if user send hour as "09", delete zero
        hours = hours[1]
    if len(minutes) == 2 and minutes[0] == '0':    # if user send minute as "09" (and etc), delete first zero
        minutes = minutes[1]
    return hours, minutes


def is_time_value(str):
    time_delimiter = ':'
    try:
        time_delimiter_ind = get_time_delimiter_ind(str, time_delimiter)
        check_hours(str, time_delimiter_ind)
        check_minutes(str, time_delimiter_ind)
        return True
    except ValueError:
        return False


def get_time_delimiter_ind(time, time_delimiter):
    ind = 0
    while ind < len(time):
        if ind == len(time) - 1:
            raise ValueError
        if time[ind] == time_delimiter:
            return ind
        ind += 1


def check_hours(time, time_delimiter_ind):
    hours = time[0:time_delimiter_ind]
    if len(hours) == 2 and hours[0] == '0':    # if user send hour as "09" (and etc), delete first zero
        hours = hours[1]
    if int(hours) < 0 or int(hours) >= 24:
        raise ValueError


def check_minutes(time, time_delimiter_ind):
    minutes = time[time_delimiter_ind + 1:len(time)]
    if len(minutes) == 2 and minutes[0] == '0':    # if user send minute as "09" (and etc), delete first zero
        minutes = minutes[1]
    if int(minutes) < 0 or int(minutes) >= 60:
        raise ValueError


# # возвращает дату дд.мм.гггг, чч:мм, интервал от текущего времени
# # ближайшего стендапа
# def get_next_standup_date(team_db_id):
#     schedule = db_teams.find_one({'_id': team_db_id})['schedule']
#     next_week_dates = get_next_week_dates()
#     pass


WEEKDAY_NUMS = {'MONDAY': 0,
                'TUESDAY': 1,
                'WEDNESDAY': 2,
                'THURSDAY': 3,
                'FRIDAY': 4,
                'SATURDAY': 5,
                'SUNDAY': 6}


# возвращает словарь с номерами дней стендапов из расписания и временем, интервалом
def get_standup_weekday_nums_with_time(schedule):
    weekday_nums = defaultdict(list)

    for standup in schedule:
        day = standup['day']
        hours = int(standup['hours'])
        mins = int(standup['minutes'])
        period = int(standup['period'])
        weekday_nums[WEEKDAY_NUMS[day]].extend([hours, mins, period])

    return weekday_nums


# возвращает даты дней подходящих под дни недели стендапов (сегодня + неделя)
# в виде словаря weekday_num: [date, date] - 2 даты если сегодняшний день
def get_next_week_dates(schedule_day_nums):
    week_dates = defaultdict(list)
    today = datetime.datetime.today()
    for i in range(8):
        weekday_date = today + datetime.timedelta(days=i)
        weekday_num = weekday_date.weekday()
        if weekday_num in schedule_day_nums:
            period = schedule_day_nums[weekday_num][2]
            date = datetime.datetime(year=weekday_date.year, month=weekday_date.month, day=weekday_date.day,
                                     hour=schedule_day_nums[weekday_num][0], minute=schedule_day_nums[weekday_num][1])
            week_dates[weekday_num].append([date, period])
    return week_dates


# вощвращает список с датами (уже по одной для каждого дня в расписании)
def get_standup_dates(next_week_dates):
    standup_dates = defaultdict()
    for day_num in next_week_dates:
        dates = next_week_dates[day_num]

        # если в расписании есть сегодняшний день, то выбираем из двух
        if len(dates) > 1:
            today = datetime.datetime.today()
            delta = []
            for date in dates:
                delta.append(date[0] - today)
            if (delta[0] < delta[1] and not delta[0].days < 0) or (delta[1] < delta[0] and delta[1].days < 0):
                standup_dates[dates[0][0]] = dates[0][1]
            else:
                standup_dates[dates[1][0]] = dates[1][1]
        else:
            standup_dates[dates[0][0]] = dates[0][1]

    return standup_dates
