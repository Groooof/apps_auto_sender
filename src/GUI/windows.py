from tkinter import *
from tkinter.ttk import *
from threading import Thread
import subprocess
from time import sleep
from .load_graph import Graph
from .styles import StylesSetter
from ..key_checker import *
from ..config import WindowConfig
from ..applications_sending import AppsSender
from ..authorization import Account
from ..database import ApplicationsDB
from ..parsing import Parser
from ..observer_pattern import *
from .applications_table import ApplicationsTable

# Main window -----------------------------------------------------------------------------------------------


class SiteBlock(LabelFrame):
    def __init__(self, parent, site,  window_data, pady=0, **kwargs):
        super().__init__(parent, height=65, **kwargs)

        label_site = Label(self, style='Light.TLabel', text=site)
        btn_params = Button(self, text='Параметры торговой площадки',
                            command=lambda: parent._new_window(window_data))

        label_site.pack(side=LEFT, padx=30)
        btn_params.pack(side=RIGHT, padx=10)
        self.pack(fill=BOTH, expand=True, padx=10, pady=pady)
        self.pack_propagate(False)


class GermesLoadBlock(LabelFrame):
    def __init__(self, parent, pady=0, **kwargs):
        super().__init__(parent, height=200, text='График нагрузки', **kwargs)

        graph = Graph(self, time_interval=60)

        graph.pack(fill=BOTH, expand=True)
        self.pack(fill=X, pady=pady, padx=10)
        self.pack_propagate(False)

        Thread(target=graph.start, daemon=True).start()


class ButtonsBlock(Frame):
    def __init__(self, parent, pady=0, **kwargs):
        super().__init__(parent, height=40, **kwargs)

        btn_settings = Button(self, text='Настройки', command='')
        btn_daily_report = Button(self, text='Сформировать суточный отчёт', command='')
        btn_germes_results = Button(self, text='Результаты работы Гермеса', command='')

        btn_settings.pack(side=LEFT)
        btn_daily_report.pack(side=RIGHT, padx=20)
        btn_germes_results.pack(side=RIGHT)

        self.pack(fill=X, side=TOP, padx=10, pady=pady)
        self.pack_propagate(False)


class MainWindow(Frame):
    def __init__(self, parent, cfg: WindowConfig, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = parent
        self.cfg = cfg
        self.logger = self.cfg.logger

        self.__set_settings()
        SiteBlock(self, 'www.sberbank_ast.ru', text='Сбербанк-АСТ', pady=10, window_data=self.cfg.global_config.sberbank)
        SiteBlock(self, 'www.roseltorg.ru', text='Единая Электронная Торговая Площадка', window_data=self.cfg.global_config.roseltorg)
        SiteBlock(self, 'www.rts-tender.ru', text='РТС-тендер', pady=10, window_data=self.cfg.global_config.rts)
        GermesLoadBlock(self)
        ButtonsBlock(self, pady=10)

        self.pack(fill=BOTH, expand=True)
        self.logger.info('Главное окно открыто')

    def _new_window(self, cfg: WindowConfig):
        app = Toplevel(self)
        account = Account(cfg)
        window = ChildWindow(app, account, cfg)
        db = ApplicationsDB(cfg)
        table = ApplicationsTable(window, db)
        parser = Parser(cfg, db)
        #app_sender = AppsSender(cfg, db)

        window.attach(table)
        window.attach(parser)
        #window.attach(app_sender)

        account.attach(table)
        account.attach(parser)
        #account.attach(app_sender)

        db.attach(table)
        #db.attach(app_sender)

        app.mainloop()

    def __set_settings(self):
        self.app.title(self.cfg.WND_TITLE)
        self.app.minsize(self.cfg.WND_MIN_WIDTH, self.cfg.WND_MIN_HEIGHT)
        self.app.geometry(f'{self.cfg.WND_MIN_WIDTH}x{self.cfg.WND_MIN_HEIGHT}')
        self.app.protocol("WM_DELETE_WINDOW", self.__on_close)
        StylesSetter().set()

    def __on_close(self):
        subprocess.call('TASKKILL /f /IM CHROMEDRIVER.EXE')
        self.app.destroy()
        self.logger.info('Главное окно закрыто')

# Child window -----------------------------------------------------------------------------------------------


class EntryField(Frame):
    def __init__(self, parent, text, show='', **kwargs):
        super().__init__(parent, **kwargs)

        self.label = Label(self, style='Light.TLabel', text=text+' :')
        self.entry = Entry(self, show=show)

        self.label.pack(side=LEFT, fill=Y)
        self.entry.pack(side=LEFT)


class AuthBlock(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text='Авторизация', height=80, **kwargs)

        self.login_field = EntryField(self, 'Login')
        self.password_field = EntryField(self, 'Password', show='*')
        self.btn_enter = Button(self, text='Enter', width=15, command=parent.on_auth_btn_click)

        self.login_field.pack(side=LEFT, padx=30)
        self.password_field.pack(side=LEFT, padx=0)
        self.btn_enter.pack(side=LEFT, padx=30)


class ChildWindow(Frame, Subject, Observer):
    def __init__(self, parent, account, config: WindowConfig):
        Subject.__init__(self)
        Frame.__init__(self, parent)

        self.app = parent
        self.cfg = config
        self.logger = self.cfg.logger
        self.account = account

        self.auth_block = AuthBlock(self)

        self.__set_settings()

        self.auth_block.pack(fill=X, pady=10, padx=10)
        self.auth_block.pack_propagate(False)
        self.pack(fill=BOTH, expand=True)
        self.logger.info(f'Окно {self.cfg.WND_TITLE} открыто')

    def __set_settings(self):
        self.app.title(self.cfg.WND_TITLE)
        self.app.minsize(self.cfg.WND_MIN_WIDTH, self.cfg.WND_MIN_HEIGHT)
        self.app.geometry(f'{self.cfg.WND_MIN_WIDTH}x{self.cfg.WND_MIN_HEIGHT}')
        self.app.protocol("WM_DELETE_WINDOW", self.__on_close)
        StylesSetter().set()

    def on_auth_btn_click(self):
        inp_login = self.auth_block.login_field.entry.get()
        inp_password = self.auth_block.password_field.entry.get()
        if not inp_login or not inp_password:
            print('Введите данные для авторизации!')
            return
        Thread(target=self.account.log_in, args=(inp_login, inp_password), daemon=True).start()
        self.auth_block.btn_enter['state'] = 'disable'

    def __on_close(self):
        self.app.destroy()
        data = {'from': 'ChildWindow',
                'event': 'close',
                'data': None
                }
        self.notify(data)
        self.logger.info(f'Окно {self.cfg.WND_TITLE} закрыто')


# Key checker window --------------------------------------------------------------------------------------------


class KeyCheckerWindow(Frame):
    def __init__(self, app, cfg: WindowConfig):
        if self.__check_date():
            app.destroy()
            return

        super().__init__(app)
        self.app = app
        self.cfg = cfg
        self.logger = self.cfg.logger
        self.styles = StylesSetter()
        self.__set_settings()

        key_label = Label(self, text='Введите ключ:', justify='center')
        self.key_entry = Entry(self)
        key_btn = Button(self, text='Activate', command=self.__check_key)

        key_label.pack(pady=5)
        self.key_entry.pack(fill=X, padx=20)
        key_btn.pack(fill=X, padx=50, pady=10)

        self.pack(fill=BOTH, expand=True)
        self.logger.info('Окно проверки ключа открыто')

    def __set_settings(self):
        self.app.title(self.cfg.WND_TITLE)
        self.app.minsize(self.cfg.WND_MIN_WIDTH, self.cfg.WND_MIN_HEIGHT)
        self.app.geometry(f'{self.cfg.WND_MIN_WIDTH}x{self.cfg.WND_MIN_HEIGHT}')
        self.app.resizable(width=False, height=False)
        self.app.protocol("WM_DELETE_WINDOW", self.__on_close)
        self.styles.set()

    def __on_close(self):
        self.app.destroy()
        self.logger.info('Окно проверки ключа закрыто')
        sys.exit()

    def __check_key(self):
        key = self.key_entry.get()
        if check_key(key):
            print('::. Ключ подходит!')
            set_new_end_date()
            self.app.destroy()
            self.logger.info('Ключ подошел')
            return
        self.logger.info('Ключ не подошел')

        self.key_entry.configure(foreground='red')
        self.app.update()
        sleep(1)
        self.key_entry.configure(foreground='#05386B')

    @staticmethod
    def __check_date():
        if check_date():
            return 1



