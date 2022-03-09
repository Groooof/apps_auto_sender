class AuthorizationApiPattern:
    def log_in(self, login, password, path_to_extension):
        pass


class ParsingApiPattern:
    def get_all(self, keywords: list = ('',), auth_cookies: dict = None):
        pass

    def get_new(self, border_app, keywords: list = ('',), auth_cookies: dict = None):
        pass


class AppsSendingApiPattern:
    def send_app(self, driver, auth_cookies, db_record, docs):
        pass

    def open_main_page(self, driver):
        pass

    def clean_leftovers(self, auth_cookies):
        pass

    # def create_draft(self, app_url):
    #     pass


class MainApiPattern:
    def __init__(self, auth_api: AuthorizationApiPattern, parsing_api: ParsingApiPattern, apps_sending_api: AppsSendingApiPattern):
        self.authorization = auth_api
        self.parsing = parsing_api
        self.apps_sending = apps_sending_api
