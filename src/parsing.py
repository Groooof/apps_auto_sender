from threading import Thread
from time import sleep
from .siteAPIs.api_patterns import MainApiPattern
from .database import ApplicationsDB
from .config import WindowConfig
from src.siteAPIs.exсeptions import *


class Parser:
    def __init__(self, config: WindowConfig, db: ApplicationsDB, parsing_freq=20):
        self.api = config.API
        self.logger = config.logger
        self.db = db
        self.freq = parsing_freq
        self.active = False
        self.keywords = self.__get_keywords(config.PARSING_KEYWORDS_FILEPATH)
        self.cookies = dict()
        self.is_first = True

    def parse_records(self):
        try:
            if self.is_first:
                self.logger.info('Начинаем парсинг (первый запуск)')
                records = self.api.parsing.get_all(self.keywords, self.cookies)
            else:
                last_app = self.db.get_last_app()
                self.logger.info(f'Начинаем парсинг (парсим до {last_app[1]})')
                records = self.api.parsing.get_new(last_app[1], self.keywords, self.cookies)
        except BadConnectionError:
            self.logger.warning('Плохое соединение с интернетом, не удалось получить данные от сервера!')
            return
        except BadResponseError as ex:
            self.logger.warning(f'Не удалось получить данные: {ex.message}')
            return
        except Exception as ex:
            self.logger.exception('Неизвестная ошибка!')

        # try:
        new_records = self.db.insert_new_apps(records)
        # except:
        #     self.logger.exception('Не удалось записать в БД')
        #     return
        self.is_first = False
        self.logger.info(f'Парсинг окончен. Найдено {len(records)} записей. Новых - {new_records}')

    def start(self):
        self.logger.info(f'Парсер запущен! Частота парсинга - {self.freq} сек.')
        self.active = True
        while self.active:
            self.parse_records()
            sleep(self.freq)

    def stop(self):
        if not self.active:
            return
        self.active = False
        self.logger.info('Парсер остановлен!')

    def update(self, data):
        if data['from'] == 'Account' and data['event'] == 'log in':
            self.cookies = data['data']['cookies']
            Thread(target=self.start, daemon=True).start()
        elif data['from'] == 'ChildWindow' and data['event'] == 'close':
            self.stop()

    @staticmethod
    def __get_keywords(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            keywords = f.readlines()
        return keywords

