

class BaseCustomException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class BadConnectionError(BaseCustomException):
    pass


class BadResponseError(BaseCustomException):
    def __init__(self, response, msg='Ответ сервера не удалось преобразовать в JSON'):
        super().__init__(msg)
        self.response = response


class CreatingDraftError(BaseCustomException):
    def __str__(self):
        return f'Ошибка при создании черновика -> {self.message}'

