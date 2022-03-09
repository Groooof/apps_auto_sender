from .. import api_patterns
import datetime, time
from time import sleep
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
from requests_toolbelt import MultipartEncoder
import random
import string
from pprint import pprint


class AuthorizationApi(api_patterns.AuthorizationApiPattern):
    def __init__(self):
        self.driver: webdriver.Chrome = None
        self.auth_page_link = 'https://etp.roseltorg.ru/authentication/login'

    def log_in(self, login, password, path_to_extension):
        try:
            self.__driver_init(path_to_extension)
            self.__get_auth_page()
            self.__get_gosuslugi_auth_page()
            self.__enter_auth_data(login, password)
            self.__send_auth_data()
            self.__wait_for_page_load()
            cookies = self.__get_cookies()
        except Exception as ex:
            raise Exception(f'Ошибка при авторизации!\n\t{ex}')
        else:
            return cookies
        finally:
            if self.driver:
                self.driver.quit()

    def __driver_init(self, extension=''):
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_extension(extension)
        self.driver = webdriver.Chrome(options=chrome_options)

    def __get_auth_page(self):
        self.driver.get(self.auth_page_link)

    def __get_gosuslugi_auth_page(self):
        checkbox_ip = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "x-form-check-wrap")][1]')))
        checkbox_ip.click()
        choose_plug_btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[text() = "Выбор плагина ЭП"]')))
        choose_plug_btn.click()
        sleep(1)
        checkbox_cryptopro = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@value = "cryptopro"]/..')))
        checkbox_cryptopro.click()
        sleep(1)
        confirm_btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[text() = "Выбрать"]')))
        confirm_btn.click()
        sleep(1)
        ok_btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[text() = "OK"]')))
        ok_btn.click()
        sleep(1)
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//span[contains(text(), "Гос")]/..')))
        btn.click()

    def __enter_auth_data(self, login, password):
        login_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@id = "login"]')))
        password_field = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//input[@id = "password"]')))
        login_field.send_keys(login)
        password_field.send_keys(password)

    def __send_auth_data(self):
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[@id = "loginByPwdButton"]')))
        btn.click()

    def __wait_for_page_load(self):
        WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//fieldset[@id = "topFieldSetUser"]')))

    def __press_esia_auth_btn(self):
        btn = WebDriverWait(self.driver, 120).until(EC.visibility_of_element_located((By.XPATH, '//button[@id = "btnEnter"]')))
        btn.click()

    def __get_cookies(self):
        cookies = {}
        for cookie in self.driver.get_cookies():
            if cookie['name'] in ('etpauth', 'etpsid', 'cert_c', 'default_url', 'ys-long_session', 'ys-lock_ip', 'ys-supplier_auction_index_advanced', 'eds_selected_plugin'): # , '_ym_uid', '_ym_d', '_ym_isad'):
                cookies[cookie['name']] = cookie['value']
        return cookies

    def __save_cookies(self, cookies):
        with open(self.cookies_file_path, 'w') as f:
            json.dump(cookies, f)


class OldParsingApi(api_patterns.ParsingApiPattern):
    def __init__(self):
        self.site_link = 'https://www.roseltorg.ru'
        self.fz44_link = '/search_ajax/44fz'
        self.keywords_path = './parse_keywords/rosel_keywords.txt'
        self.headers = {
            'authority': 'www.roseltorg.ru',
            'method': 'GET',
            'scheme': 'https',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'Host': 'www.roseltorg.ru'
            }
        self.params = {
            'source[]': '1',
            'status[]': '0',
            'currency': 'all',
            'page': '0',
            'from': '0',
            'query_field': ''
            }
        self.items = []
        self.auc_links = []
        self.page: Page = None

    def get_applications_list(self):
        print('::. Получаем ключевые слова')
        keywords = self.__get_keywords()
        print(f'::. Получено {len(keywords)} ключевых слов')
        print('::. Парсим ссылки на аукционы')
        for i, keyword in enumerate(keywords):
            # print(f'[{i+1} / {len(keywords)}]')
            print(keyword.strip())
            self.params['query_field'] = keyword.strip()
            self.__parse_auc_links()

        print(f'::. Найдено {len(self.auc_links)} ссылок')

        print('::. Парсим данные аукционов')
        for i, auc_link in enumerate(self.auc_links):
            print(f'[{i + 1} / {len(self.auc_links)}]')
            self.__get_page(self.site_link + auc_link, headers=self.headers, params=self.params)
            data = self.__get_data()
            self.__process_data(data)

        items = self.items
        self.items = []
        self.auc_links = []
        return items

    def __get_keywords(self):
        with open(self.keywords_path, 'r', encoding='utf-8') as f:
            keywords = f.readlines()
        return keywords

    def __get_data(self):
        # print(f'::. Получаем данные')
        item = {}
        item['Наименование'] = ''.join(self.page.dom.xpath('//span[text() = "Наименование процедуры"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Номер лота'] = ''.join(self.page.dom.xpath('(//h1)[1]/text()'))
        item['Цена'] = ''.join(self.page.dom.xpath('//div[@class = "lot-item__sum"]/p/text()'))
        item['Опубликовано'] = ''.join(self.page.dom.xpath('//span[text() = "Дата публикации"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Срок подачи заявок'] = ''.join(self.page.dom.xpath('//span[text() = "Дата и время окончания подачи заявок"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Срок рассмотрения заявок'] = ''.join(self.page.dom.xpath('//span[text() = "Дата и время рассмотрения заявок"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Начало аукциона'] = ''.join(self.page.dom.xpath('//span[text() = "Дата проведения торгов"]/../../td[@class = "data-table__info-td"]/p/text()'))

        return item

    def __get_page(self, link, headers=None, data=None, params=None):
        try:
            print(link)
            response = requests.get(link, headers=headers, params=params, verify=False)
        except Exception as ex:
            print(f'Не удалось загрузить страницу, пробуем ещё раз:\n{ex}')
            self.__get_page(link, headers=headers, data=data, params=params)
            return
        self.page = Page(response)

    def __next_page_exist(self):
        next_page_link = ''.join(self.page.dom.xpath('//a[@class = "pagination__btn pagination__btn--next"]/@href'))
        if not next_page_link:
            return 0
        return 1

    def __process_data(self, data):
        # print('::. Обрабатываем данные')

        data['Наименование'] = data['Наименование']
        data['Номер лота'] = '№' + data['Номер лота'].replace('Процедура:', '').strip()
        data['Цена'] = data['Цена'].replace(',', '')
        data['Опубликовано'] = ':'.join(data['Опубликовано'].split(':')[:-1]).replace('до', '').strip()
        temp = datetime.datetime.strptime(data['Опубликовано'], '%d.%m.%y %H:%M')
        data['Опубликовано_datetime'] = int(time.mktime(temp.timetuple()))
        data['Срок подачи заявок'] = ':'.join(data['Срок подачи заявок'].split(':')[:-1]).replace('до', '').strip()
        data['Срок рассмотрения заявок'] = ':'.join(data['Срок рассмотрения заявок'].split(':')[:-1]).replace('до', '').strip()
        data['Начало аукциона'] = ':'.join(data['Начало аукциона'].split(':')[:-1]).replace('до', '').strip()

        item = (data['Наименование'],
                data['Номер лота'],
                data['Цена'],
                data['Опубликовано'],
                data['Срок подачи заявок'],
                data['Срок рассмотрения заявок'],
                data['Начало аукциона'],
                0,
                data['Опубликовано_datetime'])

        if 'транспорт' in data['Наименование']:
            self.items.append(item)

    def __parse_auc_links(self):
        page = 0
        while True:
            print(f'Страница {page}')
            self.__get_page(self.site_link + self.fz44_link, headers=self.headers, params=self.params)
            links = self.__get_auc_links()
            self.auc_links.extend(links)
            next_page_exist = self.__next_page_exist()
            if not next_page_exist:
                break
            page += 1
            self.params['page'] = str(page)
            self.params['from'] = str(page*10)

    def __get_auc_links(self):
        links = []
        cards = self.page.dom.xpath('//div[@class = "search-results__item"]')
        for card in cards:
            name = ''.join(card.xpath('.//a[@class = "search-results__link"]//text()'))
            link = ''.join(card.xpath('(.//a[@class = "search-results__link"])[1]/@href'))
            if 'транспорт' in name:
                links.append(link)
        return links


class ParsingApi(api_patterns.ParsingApiPattern):
    def __init__(self):
        super().__init__()
        self.main_link = 'https://etp.roseltorg.ru'
        self.getting_apps_link = '/data/auctionlist2.php'
        self.app_page_link = '/supplier/auction/apply/auction_id/'
        self.apps_list_page_link = '/supplier/auction/index'
        self.form_data = {
            'start': '0',
            'limit': '25',
            'userId': '',
            'company_id': '',
            'keywords': '',
            'registry_number': '',
            'delivery_place': '',
            'mine_auctions': '0',
            'joint_bidding': '0',
            'no_applics': 'NaN',
            'customers_name': '',
            'organizer_region': '',
            'status': '',
            'proceduretype': 'all',
            'start_from': '',
            'start_till': '',
            'publish_from': '',
            'publish_till': '',
            'endreg_from': '',
            'endreg_till': '',
            'endfirstreview_from': '',
            'endfirstreview_till': '',
            'price_min': '',
            'price_max': '',
            'okpd': '',
            'from': 'supplier',
            'apnum': '0',
            'query': '',
            'sort': 'date_published',
            'dir': 'DESC'
            }
        self.headers = {
            'authority': 'etp.roseltorg.ru',
            'method': 'POST',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,en;q=0.9,kk;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://etp.roseltorg.ru',
            'referer': 'https://etp.roseltorg.ru/supplier/auction/index/status/31/proceduretypes/all',
            'sec-ch-ua': '"Chromium";v="94", "Yandex";v="21", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            }
        self.account_data = None
        self.is_first = False

    def get_all(self, keywords: list = ('',), auth_cookies: dict = None):
        if not auth_cookies:
            raise Exception('Отсутствуют куки авторизации!')
        if not self.account_data:
            user_id, company_id = self.__parse_account_data(auth_cookies)
            self.form_data['userId'] = user_id
            self.form_data['company_id'] = company_id

        json_apps_all = list()
        for keyword in keywords:
            json_apps_part = self.__parse_by_keyword(keyword, auth_cookies)
            json_apps_all.extend(json_apps_part)
            sleep(random.randint(3, 10))

        result = list()
        for app in json_apps_all:
            processed_app = self.__process_json_app(app)
            if processed_app: result.append(processed_app)
        return result

    def __parse_by_keyword(self, keyword, auth_cookies):
        self.form_data['limit'] = '100'
        self.form_data['keywords'] = keyword

        response = requests.post(self.main_link + self.getting_apps_link, headers=self.headers, data=self.form_data, cookies=auth_cookies)
        try:
            response_json = response.json()
        except Exception as ex:
            raise Exception(f'Сервер не вернул ни одной записи! Код ответа - {response.status_code}')

        if response_json.get('captcha'):
            raise Exception('Сервер требует капчу!')

        if 'success' in response_json and not response_json['success']:
            raise Exception(f'Сервер не вернул ни одной записи! Код ответа - {response.status_code}')

        return response_json['auctions']

    def __process_json_app(self, json_app):
        name = json_app['title']

        if 'транспорт' not in name:
            return None

        number = json_app['registry_number']
        price = json_app['price'].split(',')[0]
        public_date = str(json_app['date_published']).replace('-', '.').replace('T', ' ').split('+')[0]
        request_date = str(json_app['date_end_registration']).replace('-', '.').replace('T', ' ').split('+')[0]
        request_accept_date = str(json_app['date_end_first_part_review']).replace('-', '.').replace('T', ' ').split('+')[0]
        auction_begin_date = str(json_app['date_begin_auction']).replace('-', '.').replace('T', ' ').split('+')[0]
        status = 0
        public_date_unix = int(time.mktime((datetime.datetime.strptime(public_date, '%Y.%m.%d %H:%M:%S')).timetuple()))
        url = self.main_link + self.app_page_link + str(json_app['id'])
        processed_app = (name, number, price, public_date, request_date, request_accept_date, auction_begin_date, status, public_date_unix, url)
        return processed_app

    def __parse_account_data(self, auth_cookies):
        response = requests.get(self.main_link + self.apps_list_page_link, headers=self.headers, cookies=auth_cookies)
        source_html = response.text
        try:
            user_id = source_html.split("'userId'")[1].split("'")[1]
            company_id = source_html.split("'company_id'")[1].split("'")[1]
        except Exception as ex:
            raise Exception(f'Не удалось получить данные аккаунта:\n\t{ex}')
        return user_id, company_id

    def get_new(self, border_app, keywords: list = ('',), auth_cookies: dict = None):
        for keyword in keywords:
            source_html = self.__get_first_page(keyword)
            all_apps_nums = self.__parse_apps_nums(source_html)

            new_apps_nums = list()
            for app_num in all_apps_nums:
                if app_num == border_app: break
                new_apps_nums.append(app_num)

            result = list()
            for app_num in new_apps_nums:
                source_html = self.__get_app_page(app_num)
                app_data = self.__parse_app_data(source_html)
                processed_app_data = self.__process_app_data(app_data)
                if processed_app_data: result.append(processed_app_data)

            return result

    def __get_first_page(self, keyword):
        params = {
            'query_field': keyword,
            'source[]': '1',
            'status[]': '0',
            'currency': 'all'
            }
        url = 'https://www.roseltorg.ru/search_ajax/44fz'
        response = requests.get(url, headers={}, params=params)
        return response.text

    def __parse_apps_nums(self, source_html):
        dom = html.fromstring(source_html)
        nums = [num.split(' (')[0] for num in dom.xpath('//div[@class = "search-results__lot"]/a[@class = "search-results__link"]//text()')]
        return nums

    def __get_app_page(self, num):
        url = 'https://www.roseltorg.ru/procedure/' + num
        try:
            resposne = requests.get(url, headers={})
        except:
            # print('Trying again')
            return self.__get_app_page(num)

        return resposne.text

    def __parse_app_data(self, source_html):
        dom = html.fromstring(source_html)
        item = dict()
        item['Наименование'] = ''.join(dom.xpath('//span[text() = "Наименование процедуры"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Номер лота'] = ''.join(dom.xpath('(//h1)[1]/text()'))
        item['Цена'] = ''.join(dom.xpath('//div[@class = "lot-item__sum"]/p/text()'))
        item['Опубликовано'] = ''.join(dom.xpath('//span[text() = "Дата публикации"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Срок подачи заявок'] = ''.join(dom.xpath('//span[text() = "Дата и время окончания подачи заявок"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Срок рассмотрения заявок'] = ''.join(dom.xpath('//span[text() = "Дата и время рассмотрения заявок"]/../../td[@class = "data-table__info-td"]/p/text()'))
        item['Начало аукциона'] = ''.join(dom.xpath('//span[text() = "Дата проведения торгов"]/../../td[@class = "data-table__info-td"]/p/text()'))

        return item

    def __process_app_data(self, data):
        data['Наименование'] = data['Наименование']
        data['Номер лота'] = '№' + data['Номер лота'].replace('Процедура:', '').strip()
        data['Цена'] = data['Цена'].replace(',', '')
        data['Опубликовано'] = ':'.join(data['Опубликовано'].split(':')[:-1]).replace('до', '').strip()
        temp = datetime.datetime.strptime(data['Опубликовано'], '%d.%m.%y %H:%M')
        data['Опубликовано_datetime'] = int(time.mktime(temp.timetuple()))
        data['Срок подачи заявок'] = ':'.join(data['Срок подачи заявок'].split(':')[:-1]).replace('до', '').strip()
        data['Срок рассмотрения заявок'] = ':'.join(data['Срок рассмотрения заявок'].split(':')[:-1]).replace('до', '').strip()
        data['Начало аукциона'] = ':'.join(data['Начало аукциона'].split(':')[:-1]).replace('до', '').strip()

        item = (data['Наименование'],
                data['Номер лота'],
                data['Цена'],
                data['Опубликовано'],
                data['Срок подачи заявок'],
                data['Срок рассмотрения заявок'],
                data['Начало аукциона'],
                0,
                data['Опубликовано_datetime'])

        if 'транспорт' in data['Наименование']:
            return item
        return None


class AppsSendingApi(api_patterns.AppsSendingApiPattern):
    def __init__(self):
        super().__init__()
        self.main_link = 'https://etp.roseltorg.ru'
        self.saving_draft_link = '/supplier/auction/apply'
        self.searching_draft_link = '/data/apps.php'
        self.deleting_draft_link = '/supplier/application/delete/id/'
        self.headers = {
            'authority': 'etp.roseltorg.ru',
            'method': 'POST',
            'path': '/data/auctionlist2.php',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,en;q=0.9,kk;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://etp.roseltorg.ru',
            'referer': 'https://etp.roseltorg.ru/supplier/auction/index/status/31/proceduretypes/all',
            'sec-ch-ua': '"Chromium";v="94", "Yandex";v="21", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            #'cookie': 'PAPVisitorId=03939ef18066fcba16e00e13yKvEog5M; _ym_uid=163733918936259618; _ym_d=1637339189; _pk_ref.103.478a=%5B%22%22%2C%22%22%2C1637339189%2C%22https%3A%2F%2Fyandex.ru%2F%22%5D; _pk_id.103.478a=35b8fc8cabd1494d.1637339189.; __utmz=111127430.1637339189.1.1.utmcsr=yandex.ru|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=111127430.1927190547.1637339189.1637339189.1637339189.1; _ga=GA1.2.1927190547.1637339189; tmr_lvid=52bddd60d3dfcbc4df85d7d49d539205; tmr_lvidTS=1637339188656; _fbp=fb.1.1637339189155.852244632; cert_c=6; ys-long_session=b%3A1; _pk_id.13.1d94=48530262ab5cfd75.1637339192.; yam-cid=163733918936259618; gglm-cid=1927190547.1637339189; d6063c6489f81d8b28b9b598dcd83cb2=9b1e428b6cd3f4ec6e893fecf31981dd; googtrans=null; __utmc=111127430; utmz_main_domain=111127430.1637339189.1.1.utmcsr%3Dyandex.ru%7Cutmccn%3D%28referral%29%7Cutmcmd%3Dreferral%7Cutmcct%3D/; tmr_reqNum=6; ys-lock_ip=b%3A1; default_url=%2Fsupplier%2Fauction%2Findex; ys-supplier_auction_index_advanced=b%3A1; ys-supplier_auction_index=o%3Avalue%3Ds%253A; ys-grid_id_for_state=o%3Acolumns%3Da%253Ao%25253Aid%25253Dn%2525253A0%25255Ewidth%25253Dn%2525253A25%255Eo%25253Aid%25253Dn%2525253A1%25255Ewidth%25253Dn%2525253A129%255Eo%25253Aid%25253Dn%2525253A2%25255Ewidth%25253Dn%2525253A184%255Eo%25253Aid%25253Dn%2525253A3%25255Ewidth%25253Dn%2525253A120%255Eo%25253Aid%25253Dn%2525253A4%25255Ewidth%25253Dn%2525253A200%25255Ehidden%25253Db%2525253A1%255Eo%25253Aid%25253Dn%2525253A5%25255Ehidden%25253Db%2525253A1%255Eo%25253Aid%25253Dn%2525253A6%25255Ewidth%25253Dn%2525253A126%255Eo%25253Aid%25253Dn%2525253A7%25255Ewidth%25253Dn%2525253A90%255Eo%25253Aid%25253Dn%2525253A8%25255Ehidden%25253Db%2525253A1%255Eo%25253Aid%25253Dn%2525253A9%25255Ewidth%25253Dn%2525253A90%255Eo%25253Aid%25253Dn%2525253A10%25255Ewidth%25253Dn%2525253A90%255Eo%25253Aid%25253Dn%2525253A11%25255Ehidden%25253Db%2525253A1%255Eo%25253Aid%25253Dn%2525253A12%25255Ehidden%25253Db%2525253A1%255Eo%25253Aid%25253Dn%2525253A13%25255Ewidth%25253Dn%2525253A87%5Esort%3Do%253Afield%253Ds%25253Adate_published%255Edirection%253Ds%25253ADESC; ys-supplier_auction_index_keywords=o%3Avalue%3Ds%253A%25u041E%25u0421%25u0410%25u0413%25u041E; etpsid=IYjAS0Te3ivBXQ1tHf%2CEKQkVFIlxDu3CQ3p-nk-JtMIM5FCHQ%2CmmZb69oHud1fl5; _pk_ref.13.1d94=%5B%22%22%2C%22%22%2C1637516885%2C%22https%3A%2F%2Fwww.roseltorg.ru%2F%22%5D; _pk_ses.13.1d94=1; _ym_isad=2; _gid=GA1.2.1023516535.1637516887; _gat_gtag_UA_146888930_1=1; etpauth=OOUXTTufjqAJZ1g8GikA3RrFXi9heHf7fQw%2B%2FymD8cdTMeEAnMUsk%2FkPIY7Ka1ImeRuR%2BacPn3tEoh%2BRXe3XJJd4Qu%2FoDym%2FWdKN6IkdYeiD8Q6n7QqSm9h%2B%2Frej89sz%2Fs6YnG7Ei5Yud0LC7igT05SVNVg%3D'
        }
        self.app_types = {
            'Открытый конкурс в электронной форме': 'OK',
            'Электронный аукцион': 'EF',
            'Запрос котировок в электронной форме': 'ZK'
            }

    def open_main_page(self, driver):
        driver.get(self.main_link)

    def send_app(self, driver, auth_cookies, db_record, docs):

        if not docs.get('over_500k_confirmation'):
            raise Exception('Отсутствуют необходимые документы!')

        # Из db_record вытаскиваем номер заявки и ссылку на страницу заявки
        # Номер и ссылка всегда на 1 и -1 месте в записи
        number = db_record[1]
        url = db_record[-1]
        # Создаем черновик со всеми необходимыми параметрами при помощи запросов
        try:
            self.create_draft(url, docs, auth_cookies)
        except Exception as ex:
            # Если в процессе создания черновика возникла ошибка - вызываем исключение
            raise Exception(f'Ошибка при создании черновика!')

        # Проверяем существование черновика на самом сайте
        if not self.check_draft_creation(number, auth_cookies):
            raise Exception('Не удалось создать черновик!')

        # Открываем ранее созданный черновик в браузере, выбираем сертификат и отправляем заявку
        self.__open_app_page(url, driver)
        self.__press_sending_button(driver)
        # После нажатия кнопки отправки заявки появляется окошко с ошибкой о неправильной версии плагина,
        # нам нужно проверять его наличие, закрывать его и ещё раз нажимать кнопку
        while True:
            self.__press_confirm_button(driver)
            if not self.__check_error_wnd(driver):
                break
            self.__press_ok_button(driver)

        # Далее из появившегося списка выбираем сертификат и нажимаем ОК
        try:
            self.__choose_certificate(driver)
        except:
            raise Exception('Не удалось найти сертификат!')
        self.__press_choose_button(driver)

        # Удаляем ранее созданный черновик
        try:
            self.delete_draft(url, auth_cookies)
        except Exception as ex:
            raise Warning(f'Ошибка при удалении черновика:\n\t{ex}')

    def create_draft(self, app_url, docs, auth_cookies):
        source_html = self.__get_app_page(app_url, auth_cookies)
        source_data = self.__parse_app_page(source_html)
        form_data = self.__generate_form_data(source_data, docs)
        response_json = self.__save_draft(form_data, auth_cookies)
        if response_json['success']:
            return response_json['msg']
        return 0

    def __get_app_page(self, url, auth_cookies):
        response = requests.get(url, headers=self.headers, cookies=auth_cookies)
        return response.text

    def __parse_app_page(self, source_html):
        source_data = dict()
        app_type_rus = source_html.split("'Способ закупки:'")[1].split('html:')[1].split("'")[1]
        source_data['app_type'] = self.app_types[app_type_rus]

        application_form_html = source_html.split('var application_form = ')[1].split('];')[0] + ']'

        source_data['auction_id'] = application_form_html.split("name: 'auction_id'")[1].split('value')[1].split("'")[1]
        source_data['updated'] = application_form_html.split("name: 'updated'")[1].split('value')[1].split("'")[1]
        source_data['supplier_id'] = application_form_html.split("name: 'supplier_id'")[1].split('value')[1].split("'")[1]

        accts_html = source_html.split('var acctsStore = ')[1].split('data: ')[1].split(']}')[0] + ']}'
        accts_json = json.loads(accts_html)
        source_data['bank_id'] = accts_json['rows'][0]['bank_id']
        source_data['acct_id'] = str(accts_json['rows'][0]['id'])

        source_data['phone'] = source_html.split("name: 'phone'")[1].split('value')[1].split("'")[1]
        source_data['other_inn'] = source_html.split("'other_inn'")[1].split("'")[1]
        source_data['declaration_check'] = source_html.split("name: 'declaration_check'")[1].split('value')[1].split(" ")[1].strip()

        source_data['declaration_text'] = source_html.split("id: 'declaration_text'")[1].split('value: ')[1].split('\n')[0][1:-2]
        source_data['declaration_text'] = source_data['declaration_text'].encode('utf-8').decode('unicode_escape').strip()
        source_data['start_price'] = source_html.split('var start_price = ')[1].split('"')[1]

        if source_data['app_type'] == 'EF':
            source_data['agreement'] = source_html.split("id: 'agreement'")[1].split('value')[1].split('"')[1]
            source_data['agreement'] = source_data['agreement'].encode('utf-8').decode('unicode_escape')
            if float(source_data['start_price']) > 500000:
                source_data['manual_bank_guarantees'] = source_html.split("'manual_bank_guarantees'")[1].split("'")[1]

        if source_data['app_type'] == 'OK':
            source_data['agreement'] = source_html.split("id: 'agreement'")[1].split('value')[1].split('"')[1]
            source_data['agreement'] = source_data['agreement'].encode('utf-8').decode('unicode_escape')

        if source_data['app_type'] == 'ZK':
            pass

        return source_data

    def __generate_form_data(self, source_data, docs: dict):
        webkit_data = dict()
        webkit_data['application_id'] = ''
        webkit_data['auction_id'] = source_data['auction_id']
        webkit_data['updated'] = source_data['updated']
        webkit_data['supplier_id'] = source_data['supplier_id']
        webkit_data['bank'] = source_data['bank_id']
        webkit_data['acct'] = source_data['acct_id']
        webkit_data['origin_preferences[NOTPROVIDED]'] = 'on'
        webkit_data['oksm_countryraw'] = ''
        webkit_data['trademark[]'] = ('', '', 'application/octet-stream')
        webkit_data['files_otherp1_descr[]'] = ''
        webkit_data['files_otherp1[]'] = ('', '', 'application/octet-stream')
        webkit_data['phone'] = source_data['phone']
        webkit_data['resident'] = '1'
        webkit_data['other_inn_tmp[]'] = source_data['other_inn']
        webkit_data['files_perfomance_goods[]'] = ('', '', 'application/octet-stream')
        webkit_data['declaration_check'] = source_data['declaration_check']
        webkit_data['declaration_text'] = source_data['declaration_text']
        webkit_data['files_type4_descr[]'] = ''
        webkit_data['files_type4[]'] = ('', '', 'application/octet-stream')

        if source_data['app_type'] == 'EF':
            webkit_data['agreement'] = source_data['agreement']
            if float(source_data['start_price']) > 500000:
                webkit_data['manual_bank_guarantees_tmp[]'] = source_data['manual_bank_guarantees']

                f = open(docs['over_500k_confirmation'], 'rb')

                webkit_data['confirm[]'] = ('doc_1.jpg', f, 'image/jpeg')

        if source_data['app_type'] == 'OK':
            webkit_data['agreement'] = source_data['agreement']
            webkit_data['qftext'] = ''
            webkit_data['contract_price_offer'] = source_data['start_price']
        if source_data['app_type'] == 'ZK':
            webkit_data['contract_price_offer'] = source_data['start_price']

        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        m = MultipartEncoder(fields=webkit_data, boundary=boundary)
        self.headers['content-type'] = m.content_type
        return m

    def __save_draft(self, form_data, auth_cookies):
        response = requests.post(self.main_link + self.saving_draft_link, headers=self.headers, cookies=auth_cookies, data=form_data)
        return response.json()

    def check_draft_creation(self, number, auth_cookies):
        search_result = self.__search_draft(number, auth_cookies)
        if search_result['totalCount'] == 0:
            return 0
        return 1

    def __search_draft(self, number, auth_cookies):
        self.headers['content-type'] = 'application/x-www-form-urlencoded'
        data = {
            'start': '0',
            'limit': '50',
            'startdt': '',
            'enddt': '',
            'f_order_number': '',
            'f_title': '',
            'f_registry_number': number,
            'sort': 'date_published',
            'dir': 'DESC'
            }
        response = requests.post(self.main_link + self.searching_draft_link, headers=self.headers, cookies=auth_cookies, data=data)
        try:
            response_json = response.json()
        except Exception as ex:
            raise Exception(f'Ошибка при поиске черновика:\n\t{ex}')
        return response_json

    def delete_draft(self, number, auth_cookies):
        search_result = self.__search_draft(number, auth_cookies)
        if search_result['totalCount'] == 0:
            return 0
        draft_id = search_result['apps'][0]['id']
        response = requests.post(self.main_link + self.deleting_draft_link + str(draft_id), headers=self.headers, cookies=auth_cookies)
        return response.status_code

    def __open_app_page(self, app_url, driver):
        driver.get(app_url)

    def __press_sending_button(self, driver):
        btn = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//button[text() = "Подписать и направить заявку"]')))
        btn.click()

    def __press_confirm_button(self, driver):
        btn = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//button[text() = "Подписать и направить"]')))
        btn.click()

    def __choose_certificate(self, driver):
        btn = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "viewport")]//div[contains(@class, "scroller")]//table//tr')))
        btn.click()

    def __press_choose_button(self, driver):
        btn = WebDriverWait(driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//button[text() = "Выбрать"]')))
        btn.click()

    def __check_error_wnd(self, driver):
        try:
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  '//span[contains(text(), "Для корректной работы подписания требуется свежая версия КриптоПро")]')))
        except:
            return 0
        else:
            return 1

    def __press_ok_button(self, driver):
        btn = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//button[text() = "OK"]')))
        btn.click()


class Page:
    def __init__(self, response):
        self.html = response.text
        self.dom = html.fromstring(response.text)
        self.status_code = response.status_code
        self.url = response.url


class Api(api_patterns.MainApiPattern):
    def __init__(self):
        super().__init__(AuthorizationApi(), ParsingApi(), AppsSendingApi())
