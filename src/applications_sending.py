import traceback
from time import sleep
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .siteAPIs.api_patterns import MainApiPattern
from .observer_pattern import Observer
from .database import ApplicationsDB
from .config import WindowConfig


class AppsSender(Observer):
    def __init__(self, config: WindowConfig, db: ApplicationsDB):
        self.api: MainApiPattern = config.API
        self.docs: dict = config.DOCS
        self.cryptopro_extension_path = config.global_config.extension_path
        self.logger = config.logger
        self.db = db
        self.active = False
        self.cookies = dict()
        self.driver = None

    def send_app(self, app):
        self.logger.info(f'Начинаем подачу заявки {app[1]}')
        try:
            self.api.apps_sending.send_app(self.driver, self.cookies, app, self.docs)
        except Exception as ex:
            self.logger.exception(f'Не удалось подать заявку {app[1]}!')
            return 0
        self.logger.info(f'Заявка {app[1]} успешно подана!')
        return 1

    def start(self):
        self.logger.info('Начинаем подачу заявок!')
        self.active = True
        self.__driver_init()
        self.__open_browser()
        self.__set_driver_cookies(self.cookies)
        while self.active:
            unprocessed_apps = self.db.get_unprocessed_apps()
            if not unprocessed_apps:
                self.logger.info('Ожидаем новые заявки...')
                sleep(5)
                continue
            unprocessed_app = unprocessed_apps[0]
            success = None
            success = self.send_app(unprocessed_app)
            checkmark = '1' if success else '-1'
            self.db.set_checkmark(unprocessed_app[1], checkmark)

    def stop(self):
        if not self.active:
            return
        self.api.apps_sending.clean_leftovers(self.cookies)
        self.logger.info('Подача заявок остановлена!')
        self.active = False
        self.__close_browser()

    def update(self, data):
        if data['from'] == 'Account' and data['event'] == 'log in':
            self.cookies = data['data']['cookies']
            Thread(target=self.start, daemon=True).start()
        elif data['from'] == 'DB' and data['event'] == 'insert':
            pass
        elif data['from'] == 'ChildWindow' and data['event'] == 'close':
            Thread(target=self.stop, daemon=True)

    def __driver_init(self):
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_extension(self.cryptopro_extension_path)
        driver = webdriver.Chrome(options=chrome_options)
        self.driver = driver

    def __open_browser(self):
        self.api.apps_sending.open_main_page(self.driver)

    def __close_browser(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()
            self.driver = None

    def __set_driver_cookies(self, cookies):
        [self.driver.add_cookie({'name': key, 'value': cookies[key]}) for key in cookies.keys()]