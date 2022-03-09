import os

from .. import api_patterns
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import warnings
from time import sleep
from time import time
import json
from threading import Thread
import datetime
import time
import traceback

warnings.filterwarnings("ignore")


class AuthorizationApi(api_patterns.AuthorizationApiPattern):
    def __init__(self):
        self.driver: webdriver.Chrome = None
        self.auth_page_link = 'https://www.rts-tender.ru/login'
        self.cookies_file_path = 'auth_cookies.json'

    def __driver_init(self, path_to_extension):
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_extension(path_to_extension)
        self.driver = webdriver.Chrome(options=chrome_options)

    def log_in(self, login, password, path_to_extension):
        try:
            self.__driver_init(path_to_extension)
            self.__get_auth_page()
            self.__get_gosuslugi_auth_page()
            self.__enter_auth_data(login, password)
            self.__send_auth_data()
            self.__enter_org_cert()
            self.__send_org_cert()
            self.__wait_for_page_load()
            sleep(2)
            cookies = self.__get_cookies()
        except Exception as ex:
            raise Exception(f'Ошибка при авторизации!\n\t{ex}')
        else:
            return cookies
        finally:
            self.driver.quit()

    def __get_auth_page(self):
        print('::. Начинаем авторизацию')
        print('::. Переходим на страницу авторизации')
        self.driver.get(self.auth_page_link)
        hover = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//div[@class ="login__right-block"]')))
        ActionChains(self.driver).move_to_element(hover).perform()
        # sleep(5)
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//div[@class ="login__hidden-item"][2]')))
        btn.click()

    def __get_gosuslugi_auth_page(self):
        print('::. Переходим на страницу авторизации ГосУслуг')
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@id = "submitSignEsia"]')))
        btn.click()

    def __enter_auth_data(self, login, password):
        print('::. Вводим логин и пароль')
        login_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@id = "login"]')))
        password_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@id = "password"]')))
        login_field.send_keys(login)
        password_field.send_keys(password)

    def __send_auth_data(self):
        print('::. Отправляем логин и пароль')
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[@id = "loginByPwdButton"]')))
        btn.click()

    def __enter_org_cert(self):
        print('::. Ждём загрузки сертификата')
        btn_org = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '(//table)[1]//tr[2]')))
        btn_org.click()
        btn_cert = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '(//table)[2]//tr[2]')))
        btn_cert.click()

    def __send_org_cert(self):
        print('::. Отправляем сертификат')
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@value = "Войти"]')))
        btn.click()

    def __wait_for_page_load(self):
        WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//div[@class = "header__column"]')))

    def __get_cookies(self):
        cookies = {}
        for cookie in self.driver.get_cookies():
            if cookie['name'] in ('.Auth.Rts.P',):
                cookies[cookie['name']] = cookie['value']
        return cookies

    def __save_cookies(self, cookies):
        with open(self.cookies_file_path, 'w') as file:
            json.dump(cookies, file)


class ParsingApiOld(api_patterns.ParsingApiPattern):
    def __init__(self):
        self.driver: webdriver.Chrome = None
        self.site_link = 'https://www.rts-tender.ru'
        self.search_page_link = '/poisk/poisk-44-fz/'
        self.keywords_path = './parse_keywords/rts_keywords.txt'
        self.items = []

    def get_list(self):
        self.__driver_init()
        keywords = self.__get_keywords()
        for keyword in keywords:
            try:
                print(keyword)
                self.driver.delete_all_cookies()
                self.__get_search_page()
                self.__set_search_settings(keyword)
                self.__display_cards()
                data = self.__get_data()
                self.__process_data(data)
            except:
                print(f'Произошла ошибка при парсинге!\n{traceback.format_exc()}')
                continue
        self.driver.quit()
        items = self.items.copy()
        self.items.clear()
        return items

    def __get_keywords(self):
        with open(self.keywords_path, 'r', encoding='utf-8') as f:
            keywords = f.readlines()
        return tuple(keywords)

    def __driver_init(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("window-size=900,900")
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {'profile.default_content_setting_values':
            {'geolocation': 2, 'popups': 2,
            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2,
            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2,
            'durable_storage': 2}}
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.minimize_window()

    def __get_search_page(self):
        self.driver.get(self.site_link + self.search_page_link)

    def __enter_search_query_old(self, keyword):
        search_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@class = "search__text"]')))
        search_field.send_keys(keyword)
        search_field.send_keys(Keys.ENTER)
        search_btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[@class = "search__btn mainButtonSearch"]')))

        old_cards_count = int(self.driver.find_element_by_xpath('//span[@id = "Notifications"]//b[@class = "main-tabs__count count"]').text.replace(' ', ''))
        self.__click_btn(search_btn)

        # Ожидаем загрузки новых карточек
        while True:
            new_cards_count = int(self.driver.find_element_by_xpath(
                '//span[@id = "Notifications"]//b[@class = "main-tabs__count count"]').text.replace(' ', ''))
            if new_cards_count != old_cards_count:
                break

    def __enter_search_query(self, keyword):
        search_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@class = "search__text"]')))
        search_field.send_keys(keyword)
        search_field.send_keys(Keys.ENTER)

    def __set_search_settings(self, keyword):
        old_cards_count = int(self.driver.find_element_by_xpath('//span[@id = "Notifications"]//b[@class = "main-tabs__count count"]').text.replace(' ', ''))

        # Открываем окно настроек
        btn_settings = self.driver.find_element_by_xpath('.//i[@class = "icon-settings-edit"]')
        btn_settings.click()
        sleep(2)

        # Ставим галочки в нужных местах
        btn = WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, '//label[text() = "Искать в файлах"]')))
        btn.click()

        btn = WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, '//label[text() = "Точное соответствие"]')))
        btn.click()

        self.__enter_search_query(keyword)

        try:
            search_btn = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//button[@class = "search__btn fromModalButtonSearch"]')))
            search_btn.click()
        except:
            pass
        #self.__click_btn(search_btn)

        # Ожидаем загрузки новых карточек
        while True:
            new_cards_count = int(self.driver.find_element_by_xpath('//span[@id = "Notifications"]//b[@class = "main-tabs__count count"]').text.replace(' ', ''))
            if new_cards_count != old_cards_count:
                break

    def __modal_window_destroyer(self):
        while self.driver.service.process:
            try:
                btn_submit = self.driver.find_element_by_xpath('//button[@class = "modal-form-reset"]')
                btn_submit.location_once_scrolled_into_view
                btn_submit.click()
            except:
                sleep(1)
            else:
                break

    def __wait_for_cards_count_changing(self, cards_count_old):
        while True:
            cards_count_new = len(self.driver.find_elements_by_xpath('//div[@class = "cards"]'))
            sleep(0.5)
            if cards_count_new > cards_count_old:
                break

    @staticmethod
    def __click_btn(btn):
        for _ in range(50):
            try:
                btn.click()
            except:
                sleep(0.5)
            else:
                break
        else:
            print('::. Error: Не получается нажать кнопку.')
            return

    def __display_cards(self):
        print('::. Отображаем все карточки на странице...')
        Thread(target=self.__modal_window_destroyer).start()
        while True:
            cards_count_old = len(self.driver.find_elements_by_xpath('//div[@class = "cards"]'))

            try:
                btn_more = WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//button[@id= "load-more"]')))
            except Exception as ex:
                break

            btn_more.location_once_scrolled_into_view
            self.__click_btn(btn_more)

            self.__wait_for_cards_count_changing(cards_count_old)
        print('::. Данные отображены, начинаем парсить!')

    def __get_data(self):
        print('::. Собираем данные с карточек')
        items = self.driver.find_elements_by_xpath('//div[@class = "cards"]')
        return items

    def __process_data(self, items):
        print('::. Получаем данные из карточек')
        for item in items:
            processed_item = self.__process_item(item)
            if processed_item:
                self.items.append(processed_item)

    @staticmethod
    def __process_item(item):
        name = ''.join(item.find_element_by_xpath('.//div[@class = "card-item__title"]').text)
        if 'транспорт' not in name:
            return ()
        org = ''.join(item.find_element_by_xpath(
            './/div[@class = "card-item"]/div[@class = "card-item__organization"]//div[@class = "card-item__organization-main"]/p[1]').text).split(
            '(')[0].strip()
        number = '№' + \
                 ''.join(item.find_element_by_xpath('.//div[@class = "card-item__about"]//a').text).split('№')[1].split(
                     'в')[0].strip()
        price = ''.join(item.find_element_by_xpath('.//div[@itemprop = "price"]').get_attribute('content'))
        public_date = ':'.join(''.join(
            item.find_element_by_xpath('.//time[@itemprop = "availabilityStarts"]').get_attribute('datetime')).split(
            ':')[:-1]).strip()
        request_date = ':'.join(''.join(
            item.find_element_by_xpath('.//time[@itemprop = "availabilityEnds"]').get_attribute('datetime')).split(':')[
                                :-1]).strip()

        public_date_time = datetime.datetime.strptime(public_date, '%d.%m.%Y %H:%M')
        public_date_time = int(time.mktime(public_date_time.timetuple()))

        processed_item = (name, number, price, public_date, request_date, '', '', 0, public_date_time)
        return processed_item


class ParsingApi:
    def __init__(self):
        self.main_link = 'https://app.rts-tender.ru'
        self.getting_apps_link = self.main_link + '/supplier/lk/api/auction/search'
        self.app_page_link = self.main_link + '/supplier/lk/App504.aspx#/OpenCompetition/View/' # + trade_id
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            #'Cookie': 'customerSearchGrid=10; recommendedTradesListView=10; isGoogleAnaliticsLoad=true; _ym_uid=1629286739685295013; _ym_d=1629286739; _ga=GA1.2.1621919428.1629286739; TrustedRootCertificate.CheckUtilVersion=1.0; ai_user=SMWbE|2021-08-18T13:24:39.905Z; _fbp=fb.1.1637748268394.1651423171; Country=RU; __utma=104154051.1621919428.1629286739.1637748268.1637867280.3; __utmc=104154051; __utmz=104154051.1637867280.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __RequestVerificationToken_L2F1dGg1=_xgyhhRwc3MSmPwb-fsRR6jWOSTFbkKLT_VMm0I1HeP_LLnAR-MQgGw-P5HaK1rL5Ecoorjfptb0aAjpRje1ZmANvb1xp2N7lGivi33Pd4w1; returnUrlHash=%23%2FTrades%2FRecommendedTrades; show504NewRequirementsPanel=true; showSpecialAccountSuccessfulCreationMessage=true; hasSpecialAccount=true; showUnfairSupplierBanner=false; showSpecialAccountCreationTinkoffPromoActionBanner=false; showWinnersNotPayPromoActionBanner=false; .Auth.Sso=pio-YLnYI54izntLPRJ8556WiAENcyjskANN3y4DVvI7Ni-djZlHpl5xlAaL1ufOgyTkAwi8aYl2TyAkgtGLE_8jGEK9Suc5BCR6mElCUMVgoeSNKjNjJJEqKvoluoXQgeXpFXftVQC_hFG2ce5MhqRzkhuLlRRWoYYbK1luMEcwnaAoT2O2yCHOGjM8ht9lWR6QmZPaQAaaZd8Qf_ksDv0_jKfNw-Uor2b869u9-8hB4QrxRwDCYZ5hK9RC5gfY7JS_2fNzkcrjH6H6corCQVsxWC4nJ2CiFL04T3AgI7yDitucqx5ohrrh1mPj3MUwFAP0t3_e21uv2LtJ8C3lNfwpy8lrzpxTF__ic-3_uUNawLEhEJj7NiJtAyE1CD4E4DVHEEj9yaI5RL8QA4CYShxiIzUUHAFyodclmMuhBrECiuvQiOSdxPxxjZHWckr8fO2AEPW2uP5e0r-CJSngHN9uNaFDZTjKw8zCIhhFjQfyJXPt2S4uGbRi8TTpLNycBg0evjRpRTsv3C3vd16elw; isAccreditationOn223RequestSent=true; showAnalyticInfoReglamentWindow=false; SecurityTokenExpiredTime=%222021-11-28T20%3A45%3A58%22; .Auth.Rts.P=Td6K0SZJSV-q9G9QxSl2MwxCHDInV2AnmvHeVg-TLPBHJ8GE4oviRGQDjhT2qhH-uQ9SmDeufg2Mmbn0daG0EbJ4cCqoGb0ue0iLlSdw3SJErKysvljB_OVZMALNaEiBvIv7Ju_HqSFeY5R2rQ7eZ85SlUXwZnmt1Z0BQzNu9Yg1lvdHG-7v84j9ZDASUGxk-RdQTh1jexs2BcDx2LwNMWGYH6y2Ycpt3SN66wmkrRIbmmK8qG-F9u7zCJoTlvxXLfu3V6F1Q-LnLiZEFtaPltonBcQIUM9DrmnuKIX2mCB5zV_UgeXyCbPxWSXkMzYRftveqviSSaUSM5oPLRhcdSxwN33O4p9OnL4rZUfxuexU45P_DljAGB67He3XOApzUWL5kNyCmEkrtQjjG0XCwna9ZcCzWe_24obgabeGdnbkAN-7i6ADf03w0VnIQC05FCp9nCGk4PUrrJQKeh7sY4weP3D6lsFV0cmvzmyrcwrzv6FhEVN7gL-ZKqUViuvNLVhxuGe8L8wAF0uAL75XBc9UHwULM34ig_G3IYSAetqbXLGewcUOmnPm3BC6Ybm9D3AVAvrAKQkQ37vl-uzI8Nl017FSfEkLd3MwHFN6ZDy600rDMXSLWZtbjfa4xR2OA7bAT78UIpIdH6prmrg0OAxNC6kM2X1JT7xqKBIUaWYSWdgzLxVWmhljntCgZeohPmQfc8yBHUrnRjh3Qlzk-olH-U8nKKScVUl7chAcrrpSLb1EXCPhJ-7ZnvSBimcSpjJ5a-ouIFDM2uAKMCy0tsi_O7KYcoM80YixXrWZcYvYDStwDh_kXGcV1sPKHnqj9d61WIrm6SErLAJshlvLBEYLv6CBqT38T15vE3A4Bo5hRh4AF4wzb08tu8HCF52gmKephCJS8DLn25hai1Z3u8cKNuJ1PMj2U-oQE38Qt-IymwHrwkURLWyp4pGjh9HAPPayQq75EB81kURSqWu5KQc_FGdGZpW7pjPn1F2_S9AVF1rac2vkiIIJ5fekZeBAV2NAZZvop2UaDvtPmvdNGll4rldqnJ2P7uCjySUBh0CvIv6X6JqgbptSGdauu0oV5L2KtKbvv5UXB2mHfL3wW4xg_hPAjI9lu6U6JuKbry4lOSE516tpkOA6fOcbKlsAuZIsSOqVxhkDKfiEO5DBNYSwTraRMzS2uVSV29fwhgWp_XsLXpiGwItGE6ovBzM44YKbu6_CVkg8EcGQldJSS0YnW3GVaOb8GP3sTPe5KV4P8Z3H140xYTfXxJ_AMLCoZ3pRw6oiEkGU_h_gp5z3WnAUxCRDANWFa5hFw8PQHzEkLrz_M73-ICgsnkT3BYNBFfFI4V7hWfoqYy7E8WoIsN7703WdK3u3Vv6z7bCrYPsJ6iR-qdb4fzAat94IHgo7_Q-qaIz18JipNvI0kidraK90pTKZkzBFsOdNXcY1qDty0nEgCARq344p5mNy-HLysvoNLXGTx0OJnt3dfzfmIBJrag84oqipr8C6nRswdI4i3t6NdHzmbMmWV_N3rxNNs81QnH8TOuu-RWPz3Qt8q7wJRwk7jShWFIHezHhcWCl1mhFuVQpwIDp0fS8Gzf32dZPrNPmpE1n9bYG93WtjEw2vjxpYbG8DcaixLu2H7KhjC_OGsTIOuFCjTEjUD-B0BCmdh5AURcPcyODJ-zvy741x_TOlOvGzNr5ZerPJgkdGWKu19w8RAfJD0zeqY9frDB4diL0n0acdLs6QOt1l3zZQMAt7F-OBqmkNwJplPBk3hSKplS9i8VjiWmYWjarrQc3XjH6fWO51G2N6nYsLq8u70UpCCxioJ_iIwGMb1uzFoXIrzic5qjxnRmwhTwy1WmM155lobvmAHoKbEIl1IiAbOKZvfyN10jKOyrb7rCYG5dvycgwgbBR3aDDIhrTsWvJibUPRUtX28VVxQqhlIx0y_PznL0kyHV0a9KT7WOX6I1adCL5J6ECBUeTOQ9-CnmYhz69Lr-OefeGA1lwDiX6Y0kMfV7vcznIFHUlqHcbtkZ3fAjAyAU1jPNZhIblOglGtzfcR_wDb15hPt7yuD-RO-MpjV254NcM9zdlTrfd9et5sqXdXI85Wh8WUVv3UTnL-k0HEo35Gl6yH4haIk-S9kqpT8YSbTjN2MKOaJo1t09x4wY0rTXy2Eu9dQids_TzGaCZGmz-AOmQUqaVezJuSbWFfWy_1K1j6RS8x9QW_RhYGjYRF2LPg7FeftrXmAQ_uF9TqrEwdmhLWR7WMqXENNkizvML2KZeCZDNbWbbI8RWxr8RVY1RMzaqz9WIruV0UbsYbCMi37nxlm96CntLAeNWHAnc2WA38NPS_1qH9b_f3D1zVchYRhPJQnBIeba9VVPstHz8uFp-H3qmX6X89hHW-WfzU8S1OF5k3hcRW2par6PEXNQz9_QgvAQpRJAZP6XCJnDQcKFEfOJEE0w; _ym_visorc=w; _ym_isad=2; _gid=GA1.2.1315729237.1638115341; ai_session=/evhq|1638115338776|1638115371406.6; OPENED_MENU_ID_COOKIE_NAME=-1',
            'Host': 'app.rts-tender.ru',
            'Origin': 'https://app.rts-tender.ru',
            'Referer': 'https://app.rts-tender.ru/supplier/auction/Trade/Search.aspx',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'x-ms-request-id': 'jot69',
            'x-ms-request-root-id': 'qFeuS',
            'X-Requested-With': 'XMLHttpRequest'
            }
        self.form_data = {
            "notificationNumber": "null",
            "name": "ОСАГО",
            "aggregateServicePurchaseSelectedTab": "1",
            "aggregateServicePurchaseStates": [1, 18, 20],
            "kladrCodeRegion": "-1",
            "collectivePurchasing": "null",
            "hasComplaint": "null",
            "organizer": "null",
            "useOrganizerName": "true",
            "useOrganizerInn": "null",
            "customer": "null",
            "useCustomerName": "true",
            "useCustomerInn": "null",
            "startPriceMin": "",
            "startPriceMax": "",
            "favorite": "null",
            "publicationDate": {
                "from": "null",
                "to": "null"
            },
            "applicationEndDate":{
                "from": "null",
                "to": "null"
            },
            "tradingDate":{
                "from": "null",
                "to": "null"},
            "aggregateProcedureTypes": ["106", "109", "102"],
            "aggregateCustomerLevels": [],
            "okpd2Codes": "null",
            "ktruCode": "null",
            "_search": "false",
            "nd": "1637867377020",
            "pageSize": "10",
            "pageNumber": "1",
            "sortingMethod": "",
            "sortingDirection": "asc"
        }

    def get_all(self, keywords: list = ('',), auth_cookies: dict = None):
        if not auth_cookies:
            raise Exception('Отсутствуют куки авторизации!')
        json_apps_all = list()
        for keyword in keywords:
            json_apps_part = self.__parse_by_keyword(keyword.strip(), auth_cookies)
            json_apps_all.extend(json_apps_part)
            sleep(2)

        result = list()
        for app in json_apps_all:
            processed_app = self.__process_json_app(app)
            if processed_app: result.append(processed_app)
        return result

    def __parse_by_keyword(self, keyword, auth_cookies):
        self.form_data['name'] = keyword
        self.form_data['pageSize'] = 70
        prepared_form_data = str(self.form_data).replace("'", '"').replace('"null"', 'null').replace('"true"', 'true').replace('"false"', 'false')
        response = requests.post(self.getting_apps_link, headers=self.headers,
                                 data=prepared_form_data.encode('utf-8'),
                                 cookies=auth_cookies, verify=False)
        try:
            response_json = response.json()
        except Exception as ex:
            raise Exception(f'Сервер не вернул ни одной записи! Код ответа - {response.status_code}')

        if not response_json['Success']:
            raise Exception(f'Сервер не вернул ни одной записи! Код ответа - {response.status_code}')

        return response_json['Data']['Data']

    def __process_json_app(self, json_app):
        name = json_app['Name']

        if 'транспорт' not in name:
            return None

        number = json_app['NotificationNumber']
        price = json_app['StartPriceString'].split(',')[0]
        public_date = str(json_app['PublicationDateString']).split(' (')[0]
        request_date = str(json_app['ApplicationEndDateString']).split(' (')[0]
        request_accept_date = None
        auction_begin_date = str(json_app['TradingStartDateString']).split(' (')[0]
        status = 0
        public_date_unix = int(time.mktime((datetime.datetime.strptime(public_date, '%d.%m.%Y %H:%M')).timetuple()))
        url = self.main_link + str(json_app['ApplicationNavigationUrl'])
        processed_app = (name, number, price, public_date, request_date, request_accept_date,
                         auction_begin_date, status, public_date_unix, url)
        return processed_app

    def get_new(self, border_app, keywords: list = ('',), auth_cookies: dict = None):
        return self.get_all(keywords, auth_cookies)


class AppsSendingApi(api_patterns.AppsSendingApiPattern):
    def __init__(self):
        self.main_link = 'https://app.rts-tender.ru'
        self.app_types = {'Электронный аукцион (71 ФЗ)': 'EF',
                          'Открытый конкурс в электронной форме': 'OK',
                          'Электронный запрос котировок': 'ZK'
                          }

    def open_main_page(self, driver):
        driver.get(self.main_link)

    def send_app(self, driver, auth_cookies, db_record, docs):
        url = db_record[-1]
        self.open_app_page(driver, url)

        if self.skip_draft(driver):
            self.open_app_page(driver, url)

        app_type = self.get_app_type(driver)

        self.set_checkmark_product_lack(driver)
        self.set_inn(driver)

        if app_type == 'ZK' or app_type == 'OK':
            self.set_contract_price(driver)

        self.set_bank(driver)

        if app_type == 'OK':
            self.load_required_docs(driver, docs['uniform_requirements'])

        if app_type == 'ZK':
            self.press_generate_declaration(driver)

        self.press_apply_btn(driver)
        self.press_yes_btn(driver)
        try:
            self.wait_for_app_sending(driver)
        except:
            raise Exception('Ошибка при подписании заявки')

    def open_app_page(self, driver, app_url):
        driver.get(app_url)
        self.wait_for_app_load(driver)

    def skip_draft(self, driver):
        self.wait_for_app_load(driver)
        try:
            make_changes_btn = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, '//button[contains(text(), "Внести изменения")]')))
        except Exception as ex:
            return 0
        make_changes_btn.click()
        self.wait_for_app_load(driver)
        del_draft_btn = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, '//button[contains(text(), "Удалить черновик")]')))
        del_draft_btn.click()
        self.wait_for_app_load(driver)
        self.press_yes_btn(driver)
        self.press_ok_btn(driver)
        return 1

    def wait_for_app_load(self, driver):
        WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//h1[contains(text(), "Заявка")]')))

    def get_app_type(self, driver):
        app_type_text = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//td[text() = "Способ закупки"]/../td[2]'))).text
        return self.app_types[app_type_text]

    def set_checkmark_product_lack(self, driver):
        checkmark = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@name = "countrySelectionSelectedBySupplier"]')))
        if not checkmark.is_selected():
            checkmark.click()

    def set_inn(self, driver):
        base_inn =WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//td[contains(text(), "Идентификационный номер налогоплательщика")]/../td[2]'))).text

        inn_field = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//textarea[@name = "InnExecutive"]')))
        inn_field.send_keys(base_inn)

    def set_bank(self, driver):
        bank_select_elem = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//td[text() = "Название банка"]/../td[2]//select')))
        bank_select_obj = Select(bank_select_elem)
        bank_select_obj.select_by_index(1)

    def press_apply_btn(self, driver):
        apply_btn = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@id = "btnApplyTop"]')))
        apply_btn.click()

    def press_ok_btn(self, driver):
        ok_btn = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//button/span[text() = "OK"]')))
        ok_btn.click()

    def press_yes_btn(self, driver):
        yes_btn = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//button/span[text() = "Да"]')))
        yes_btn.click()

    def set_contract_price(self, driver):
        max_price = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//td[text() = "Начальная (максимальная) цена контракта"]/../td[2]'))).text.replace(' руб.', '')
        contract_price_field = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//td[contains(text(), "Предложение о цене контракта")]/../td[2]/input')))
        contract_price_field.send_keys(max_price)

    def press_generate_declaration(self, driver):
        gen_declaration_btn = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//label[text() = "Сформировать декларацию"]')))
        gen_declaration_btn.click()

    def load_required_docs(self, driver, filename):
        load_input = driver.find_element_by_xpath('//div[@ng-if = "requiredDocuments"]//input[@type = "file"]')
        print(load_input.get_attribute('value'))
        load_input.send_keys(os.getcwd() + filename)
        print(load_input.get_attribute('value'))

    def wait_for_app_sending(self, driver):
        WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@id = "dialogSuccessMessage"]')))


class Api(api_patterns.MainApiPattern):
    def __init__(self):
        super().__init__(AuthorizationApi(), ParsingApi(), AppsSendingApi())
