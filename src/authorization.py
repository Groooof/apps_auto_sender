from .siteAPIs.api_patterns import MainApiPattern
from .observer_pattern import Subject
from .config import WindowConfig
from selenium.common.exceptions import TimeoutException


# сделать класс для браузера
class Account(Subject):
    def __init__(self, config: WindowConfig):
        super().__init__()
        self.__login = str()
        self.__password = str()
        self.api: MainApiPattern = config.API
        self.logger = config.logger
        self.cryptopro_extension = config.global_config.extension_path

    def log_in(self, login, password):
        # login = '79253943707'
        # password = 'Haji-1985'
        self.logger.info(f'Начинаем авторизацию для "{login}"')
        try:
            cookies = self.api.authorization.log_in(login, password, self.cryptopro_extension)
        except TimeoutException:
            self.logger.warning(f'Не удалось загрузить одну из страниц. Проверьте соединение с интернетом')
            return
        except:
            self.logger.exception('Неизвестная ошибка!')
            return

        self.__login = login
        self.__password = password
        self.logger.info(f'Авторизация прошла успешно!')
        data = {'from': 'Account',
                'event': 'log in',
                'data': {'cookies': cookies}
                }
        self.notify(data)
