from .siteAPIs.api_patterns import MainApiPattern
from .siteAPIs import sber_api
from .siteAPIs import rosel_api
from .siteAPIs import rts_api
import logging
import os


class WindowConfig:
    def __init__(self, global_config):
        self.WND_TITLE = None
        self.WND_MIN_WIDTH = None
        self.WND_MIN_HEIGHT = None
        self.DB_TABLE_NAME = None
        self.API: MainApiPattern = None
        self.PARSING_KEYWORDS_FILEPATH = None
        self.DOCS: dict = None
        self.logger: logging.Logger = None
        self.global_config = global_config


def get_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(f'./logs/{filename}', encoding='utf-8', mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(message)s',
                                  datefmt='%d-%m-%Y %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class MainWindowConfig:
    def __init__(self, global_config):
        self.WND_TITLE = 'Гермес'
        self.WND_MIN_WIDTH = 1000
        self.WND_MIN_HEIGHT = 500
        self.logger = get_logger('main_window', 'main_wnd_logs.log')
        self.global_config = global_config


class SberWindowConfig:
    def __init__(self, global_config):
        self.WND_TITLE = 'Sberbank'
        self.WND_MIN_WIDTH = 1000
        self.WND_MIN_HEIGHT = 500

        self.DB_TABLE_NAME = 'sber_records'

        self.API = sber_api()
        self.PARSING_KEYWORDS_FILEPATH = './data/parse_keywords/sber_keywords.txt'
        self.DOCS = {}
        self.logger = get_logger('sber_window', 'sber_wnd_logs.log')
        self.global_config = global_config


class RoselWindowConfig:
    def __init__(self, global_config):
        self.WND_TITLE = 'Roseltorg'
        self.WND_MIN_WIDTH = 1000
        self.WND_MIN_HEIGHT = 500

        self.DB_TABLE_NAME = 'rosel_records'

        self.API = rosel_api()
        self.PARSING_KEYWORDS_FILEPATH = './data/parse_keywords/rosel_keywords.txt'
        self.DOCS = {'over_500k_confirmation': os.getcwd() + '/data/files/rosel_over_500000.jpg'}
        self.logger = get_logger('rosel_window', 'rosel_wnd_logs.log')
        self.global_config = global_config


class RtsWindowConfig:
    def __init__(self, global_config):
        self.WND_TITLE = 'Rts'
        self.WND_MIN_WIDTH = 1000
        self.WND_MIN_HEIGHT = 500

        self.DB_TABLE_NAME = 'rts_records'

        self.API = rts_api()
        self.PARSING_KEYWORDS_FILEPATH = './data/parse_keywords/rts_keywords.txt'
        self.DOCS = {'uniform_requirements': os.getcwd() + '/data/files/uniform_requirements.txt'}
        self.logger = get_logger('rts_window', 'rts_wnd_logs.log')
        self.global_config = global_config


class KeyCheckerWindowConfig:
    def __init__(self, global_config):
        self.VERSION = '3.5'
        self.KEY = 'gV9a-aS1j-mP09-1ddX'

        self.WND_TITLE = 'Проверка ключа'
        self.WND_MIN_WIDTH = 200
        self.WND_MIN_HEIGHT = 100
        self.logger = get_logger('key_checker_window', 'key_checker_wnd_logs.log')
        self.global_config = global_config


class Config:
    def __init__(self):
        self.main = MainWindowConfig(self)
        self.sberbank = SberWindowConfig(self)
        self.roseltorg = RoselWindowConfig(self)
        self.rts = RtsWindowConfig(self)
        self.key_checker = KeyCheckerWindowConfig(self)
        self.db_path = './data/SQL/records.db'
        self.extension_path = './data/cryptopro_plug.zip'


# self.main = MainWindowConfig(self)
# ...
# __init__(self, global_cfg)
