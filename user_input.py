def is_integer_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_natural_number(string):
    try:
        number = int(string)
        if number <= 0:
            return False
        else:
            return True
    except ValueError:
        return False
