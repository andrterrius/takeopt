class ChoiceException(Exception):
    """Базовое исключение для выбора"""
    pass


class LimitChoiceException(ChoiceException):
    """Превышен лимит выборов"""
    pass


class ThrottlingChoiceException(ChoiceException):
    """Слишком частые запросы"""
    pass


class CancelChoiceException(ChoiceException):
    """Ошибка отмены выбора"""
    pass