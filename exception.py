# Общий класс исключений, сообщения которых нужно вывести пользователю
class BotUserException(BaseException):
    def __init__(self, message):
        self.message = message
