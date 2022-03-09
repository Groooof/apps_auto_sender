from .. import api_patterns
from ..exсeptions import *
import datetime
import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
from selenium.common.exceptions import TimeoutException

# -------------------------------------------------------------------------------------------


class AuthorizationApi(api_patterns.AuthorizationApiPattern):
    def __init__(self):
        self.driver: webdriver.Chrome = None
        self.main_page_link = 'https://www.sberbank-ast.ru/'
        self.cookies_file_path = 'auth_cookies.json'

    def log_in(self, login, password, path_to_extension):
        try:
            self.__driver_init()
            self.__get_main_page()
            self.__get_auth_page()
            self.__get_gosuslugi_auth_page()
            self.__enter_auth_data(login, password)
            self.__send_auth_data()
            self.__press_esia_auth_btn()
            cookies = self.__get_cookies()
        except:
            raise
        else:
            return cookies
        finally:
            self.driver.quit()

    def __driver_init(self):
        chrome_options = Options()
        chrome_options.add_argument('start-maximized')
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # chrome_options.add_extension('cryptopro_plug.zip')
        self.driver = webdriver.Chrome(options=chrome_options)

    def __get_main_page(self):
        self.driver.get(self.main_page_link)

    def __get_auth_page(self):
        btn = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class = "master_open_login"]')))
        btn.click()

    def __get_gosuslugi_auth_page(self):
        btn = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//a[@id = "mainContent_lbEsiaLogin"]')))
        btn.click()

    def __enter_auth_data(self, log, pas):
        login_field = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@id = "login"]')))
        password_field = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@id = "password"]')))
        login_field.send_keys(log)
        password_field.send_keys(pas)

    def __send_auth_data(self):
        btn = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//button[@id = "loginByPwdButton"]')))
        btn.click()

    def __press_esia_auth_btn(self):
        btn = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_element_located((By.XPATH, '//button[@id = "btnEnter"]')))
        btn.click()

    def __get_cookies(self):
        cookies = {}
        for cookie in self.driver.get_cookies():
            if cookie['name'] in ('FedAuth1', 'FedAuth', 'ASP.NET_SessionId'):
                cookies[cookie['name']] = cookie['value']
        return cookies

    def __save_cookies(self, cookies):
        with open(self.cookies_file_path, 'w') as f:
            json.dump(cookies, f)

# -------------------------------------------------------------------------------------------


class ParsingApi(api_patterns.ParsingApiPattern):
    def __init__(self):
        self.site_link = 'https://www.sberbank-ast.ru'
        self.table_link = '/SearchQuery.aspx?name=Main'
        self.headers = {
            'authority': 'www.sberbank_ast.ru',
            'method': 'POST',
            'path': '/SearchQuery.aspx?name=Main',
            'scheme': 'https',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': 'ASP.NET_SessionId=ruca4krbiuztpd5hao2eb1ns; _ym_uid=1628509227531503297; _ym_d=1628509227; _ym_isad=1; es_nonathorized_last_filters|ESPurchaseList=%3Cfilters%3E%3CmainSearchBar%3E%3Cvalue%3E%3C%2Fvalue%3E%3Ctype%3Ebest_fields%3C%2Ftype%3E%3Cminimum_should_match%3E100%25%3C%2Fminimum_should_match%3E%3C%2FmainSearchBar%3E%3CpurchAmount%3E%3Cminvalue%3E%3C%2Fminvalue%3E%3Cmaxvalue%3E%3C%2Fmaxvalue%3E%3C%2FpurchAmount%3E%3CPublicDate%3E%3Cminvalue%3E%3C%2Fminvalue%3E%3Cmaxvalue%3E%3C%2Fmaxvalue%3E%3C%2FPublicDate%3E%3CPurchaseStageTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FPurchaseStageTerm%3E%3CSourceTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FSourceTerm%3E%3CRegionNameTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FRegionNameTerm%3E%3CRequestStartDate%3E%3Cminvalue%3E%3C%2Fminvalue%3E%3Cmaxvalue%3E%3C%2Fmaxvalue%3E%3C%2FRequestStartDate%3E%3CRequestDate%3E%3Cminvalue%3E%3C%2Fminvalue%3E%3Cmaxvalue%3E%3C%2Fmaxvalue%3E%3C%2FRequestDate%3E%3CAuctionBeginDate%3E%3Cminvalue%3E%3C%2Fminvalue%3E%3Cmaxvalue%3E%3C%2Fmaxvalue%3E%3C%2FAuctionBeginDate%3E%3Cokdp2MultiMatch%3E%3Cvalue%3E%3C%2Fvalue%3E%3C%2Fokdp2MultiMatch%3E%3Cokdp2tree%3E%3Cvalue%3E%3C%2Fvalue%3E%3CproductField%3E%3C%2FproductField%3E%3CbranchField%3E%3C%2FbranchField%3E%3C%2Fokdp2tree%3E%3Cclassifier%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2Fclassifier%3E%3CorgCondition%3E%3Cvalue%3E%3C%2Fvalue%3E%3C%2ForgCondition%3E%3CorgDictionary%3E%3Cvalue%3E%3C%2Fvalue%3E%3C%2ForgDictionary%3E%3Corganizator%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2Forganizator%3E%3CCustomerCondition%3E%3Cvalue%3E%3C%2Fvalue%3E%3C%2FCustomerCondition%3E%3CCustomerDictionary%3E%3Cvalue%3E%3C%2Fvalue%3E%3C%2FCustomerDictionary%3E%3Ccustomer%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2Fcustomer%3E%3CPurchaseTypeNameTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FPurchaseTypeNameTerm%3E%3CBranchNameTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FBranchNameTerm%3E%3CIsSMPTerm%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FIsSMPTerm%3E%3CAdRequirementEnable%3E%3Cvalue%3E%3C%2Fvalue%3E%3Cvisiblepart%3E%3C%2Fvisiblepart%3E%3C%2FAdRequirementEnable%3E%3Cstatistic%3E%3CtotalProc%3E8%20325%20345%3C%2FtotalProc%3E%3CTotalSum%3E19.78%20%D0%A2%D1%80%D0%BB%D0%BD.%3C%2FTotalSum%3E%3CDistinctOrgs%3E69%20521%3C%2FDistinctOrgs%3E%3C%2Fstatistic%3E%3C%2Ffilters%3E',
            'origin': 'https://www.sberbank-ast.ru',
            'referer': 'https://www.sberbank-ast.ru/purchaseList.aspx',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.EF_link = 'https://www.sberbank-ast.ru/tradezone/supplier/PurchaseRequestEF.aspx?purchID={purch_id}'
        self.ZK_link = 'https://www.sberbank-ast.ru/tradezone/supplier/ZK/PurchaseRequest20.aspx?purchID={purch_id}'
        self.OK_link = 'https://www.sberbank-ast.ru/tradezone/supplier/OK/PurchaseRequest.aspx?purchID={purch_id}'

        self.xml_data = '''<elasticrequest>
                        <personid>0</personid>
                        <buid>0</buid>
                        <filters>
                            <mainSearchBar>
                                <value>search</value>
                                <type>best_fields</type>
                                <minimum_should_match>100%</minimum_should_match>
                            </mainSearchBar>
                            <purchAmount>
                                <minvalue></minvalue>
                                <maxvalue></maxvalue>
                            </purchAmount>
                            <PublicDate>
                                <minvalue></minvalue>
                                <maxvalue></maxvalue>
                            </PublicDate>
                            <PurchaseStageTerm>
                                <value>Подача заявок</value>
                                <visiblepart>Подача заявок</visiblepart>
                            </PurchaseStageTerm>
                            <SourceTerm>
                                <value></value>
                                <visiblepart></visiblepart>
                            </SourceTerm>
                            <RegionNameTerm>
                                <value></value>
                                <visiblepart></visiblepart>
                            </RegionNameTerm>
                            <RequestStartDate>
                                <minvalue></minvalue>
                                <maxvalue></maxvalue>
                            </RequestStartDate>
                            <RequestDate>
                                <minvalue></minvalue>
                                <maxvalue></maxvalue>
                            </RequestDate>
                            <AuctionBeginDate>
                                <minvalue></minvalue>
                                <maxvalue></maxvalue>
                            </AuctionBeginDate>
                            <okdp2MultiMatch>
                                <value></value>
                            </okdp2MultiMatch>
                            <okdp2tree>
                                <value></value>
                                <productField></productField>
                                <branchField></branchField>
                            </okdp2tree>
                            <classifier>
                                <visiblepart></visiblepart>
                            </classifier>
                            <orgCondition>
                                <value></value>
                            </orgCondition>
                            <orgDictionary>
                                <value></value>
                            </orgDictionary>
                            <organizator>
                                <visiblepart></visiblepart>
                            </organizator>
                            <CustomerCondition>
                                <value></value>
                            </CustomerCondition>
                            <CustomerDictionary>
                                <value></value>
                            </CustomerDictionary>
                            <customer>
                                <visiblepart></visiblepart>
                            </customer>
                            <PurchaseTypeNameTerm>
                                <value></value>
                                <visiblepart></visiblepart>
                            </PurchaseTypeNameTerm>
                            <BranchNameTerm>
                                <value></value>
                                <visiblepart></visiblepart>
                            </BranchNameTerm>
                            <IsSMPTerm>
                                <value></value>
                                <visiblepart></visiblepart>
                            </IsSMPTerm>
                            <AdRequirementEnable>
                                <value></value>
                                <visiblepart></visiblepart>
                            </AdRequirementEnable>
                        </filters>
                        <_source>
                            <field>TradeSectionId</field>
                            <field>purchAmount</field>
                            <field>purchCurrency</field>
                            <field>purchCodeTerm</field>
                            <field>PurchaseTypeName</field>
                            <field>purchStateName</field>
                            <field>OrgName</field>
                            <field>SourceTerm</field>
                            <field>PublicDate</field>
                            <field>RequestDate</field>
                            <field>RequestStartDate</field>
                            <field>RequestAcceptDate</field>
                            <field>EndDate</field>
                            <field>AuctionBeginDate</field>
                            <field>CreateRequestHrefTerm</field>
                            <field>CreateRequestAlowed</field>
                            <field>purchName</field>
                            <field>BidName</field>
                            <field>SourceHrefTerm</field>
                            <field>objectHrefTerm</field>
                            <field>needPayment</field>
                            <field>IsSMP</field>
                            <field>isIncrease</field>
                            <field>purchType</field>
                        </_source>
                        <sort>
                            <value>default</value>
                            <direction></direction>
                        </sort>
                        <aggregations>
                            <empty>
                                <filterType>filter_aggregation</filterType>
                                <field></field>
                            </empty>
                        </aggregations>
                        <size></size>
                        <from></from>
                    </elasticrequest>'''

    def get_all(self, keywords: list = ('',), auth_cookies: dict = None):
        items = []
        for keyword in keywords:
            data = self.__get_data(keyword.strip())
            if not data: continue
            processed_data = self.__process_data(data)
            items.extend(processed_data)
        return items

    def __process_data(self, data):
        dom = html.fromstring(data)
        items_xml = dom.xpath('//hits')
        items = []
        for item_xml in items_xml:
            # name = item_xml.xpath('.//orgname//text()')[0]
            name = item_xml.xpath('.//bidname//text()')[0]
            number = item_xml.xpath('.//purchcode//text()')[0]
            price = item_xml.xpath('.//purchamountrub//text()')[0]
            public_date = item_xml.xpath('.//publicdate//text()')[0]
            request_date = item_xml.xpath('.//requestdate//text()')[0]
            request_accept_date = item_xml.xpath('.//requestacceptdate//text()')[0]
            auction_begin_date = item_xml.xpath('.//auctionbegindate//text()')[0]
            public_date_time = datetime.datetime.strptime(public_date, '%d.%m.%Y %H:%M')
            public_date_time = int(time.mktime(public_date_time.timetuple()))

            purch_id = item_xml.xpath('.//purchid//text()')[0]
            purch_type = item_xml.xpath('.//purchtype//text()')[0].split('-')[0]
            url = str()
            if purch_type == 'EF':
                url = self.EF_link.format(purch_id=purch_id)
            elif purch_type == 'OK':
                url = self.OK_link.format(purch_id=purch_id)
            elif purch_type == 'ZK':
                url = self.ZK_link.format(purch_id=purch_id)

            items.append((name,  # Наименование организации
                          number,  # Номер контракта
                          price,  # Сумма
                          public_date,  # Опубликовано
                          request_date,  # Дата и время окончания срока подачи заявок
                          request_accept_date,  # Дата окончания срока рассмотрения заявок
                          auction_begin_date,  # Дата и время проведения электронного аукциона
                          0,  # Статус заявки (не подана)
                          public_date_time,  # Опубликовано (в формате unix)
                          url  # Ссылка на заявку
                          ))

        return items

    def __get_data(self, keyword):
        xml_data = self.__form_xmldata(keyword, 50)
        resp_data = {
            'xmlData': xml_data,
            'orgId': '0',
            'targetPageCode': 'ESPurchaseList'
        }
        try:
            response = requests.post(self.site_link + self.table_link, headers=self.headers, data=resp_data)
            response_json = json.loads(response.text)
            result = response_json['result']
        except requests.ConnectionError:
            raise BadConnectionError('Плохое соединение с интернетом')
        except json.decoder.JSONDecodeError:
            raise BadResponseError('Неожиданный ответ от сервера (ошибка)')
            # return self.__get_data(keyword)
        if result != 'success':
            raise BadResponseError('Сервер вернул ошибку')

        data = json.loads(response_json['data'])
        return data['tableXml']

    def __form_xmldata(self, search_query, records_count):
        tag_from = 0
        tag_size = records_count
        return self.xml_data. \
            replace('<size></size>', f'<size>{tag_size}</size>'). \
            replace('<from></from>', f'<from>{tag_from}</from>'). \
            replace('<value>search</value>', f'<value>{search_query}</value>')

    def get_new(self, border_app, keywords: list = ('',), auth_cookies: dict = None):
        return self.get_all(keywords, auth_cookies)

# -------------------------------------------------------------------------------------------


class AppsSendingApi(api_patterns.AppsSendingApiPattern):
    def __init__(self):
        self.headers_get = {
            'authority': 'www.sberbank_ast.ru',
            'method': 'GET',
            'path': '/tradezone/supplier/OK/PurchaseRequest.aspx?purchID=8499361',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.sberbank-ast.ru/purchaseList.aspx',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
        }
        self.headers_post = {
            'authority': 'www.sberbank_ast.ru',
            'method': 'POST',
            'path': '/tradezone/supplier/PurchaseRequestEF.aspx?purchID=8497207',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-length': '26656',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.sberbank-ast.ru',
            'referer': 'https://www.sberbank-ast.ru/tradezone/supplier/PurchaseRequestEF.aspx?purchID=8497207',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
            }
        self.source_data = {}
        self.data_for_xml = {}
        self.xml_templates_paths = {'EF': './data/xml_templates/sberbank_ast/sber_EF_xml.txt',
                                    'ZK': './data/xml_templates/sberbank_ast/sber_ZK_xml.txt',
                                    'OK': './data/xml_templates/sberbank_ast/sber_OK_xml.txt'
                                    }
        self.main_url = 'https://www.sberbank-ast.ru'
        self.drafts_page_url = self.main_url + '/tradezone/Documents/Drafts.aspx'

    def open_main_page(self, driver):
        driver.get(self.main_url)

    def clean_leftovers(self, auth_cookies):
        self.delete_all_drafts(auth_cookies)

    def send_app(self, driver, auth_cookies, db_record, docs):
        # try:
            link = db_record[-1]
            number = db_record[1].replace('№', '')

            self.create_draft(link, auth_cookies)
            self.open_draft(driver, number, auth_cookies)
            self.__check_certificate(driver)
            self.__press_send_btn(driver)

        # except Exception as ex:
        #     raise Exception(f'Ошибка при подаче заявки:\n\t{ex}')

# Отправка заявки ----------------------------------------------------------------------------------------------------

    def __check_certificate(self, driver: WebDriver):
        try:
            cert_name = WebDriverWait(driver, 300).until(
                EC.visibility_of_element_located((By.XPATH, '//select[@id = "ctl00_ctl00_phWorkZone_SignPanel_certList"]/option'))).text
        except:
            raise Exception('Не удалось обнаружить сертификат!')
        else:
            return cert_name

    def __press_send_btn(self, driver):
        try:
            btn = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//input[@id = "SignPanel_btnSignAllFilesAndDocument"]')))
            btn.click()
        except Exception as ex:
            raise Exception(f'Не удалось нажать кнопку для подачи заявки!\n{ex}')

# Создание черновика -------------------------------------------------------------------------------------------------

    def create_draft(self, app_url, auth_cookies):
        app_type = self.__define_app_type(app_url)

        source_html = self.__get_app_page(app_url, auth_cookies)
        try:
            self.__parse_app_page(source_html)
            self.__parse_app_xml(self.source_data['xml_data'], app_type)
        except:
            raise CreatingDraftError('Не удалось найти на странице нужные данные')
        data = self.__generate_creating_draft_form_data(app_type)

        try:
            response = requests.post(app_url, headers=self.headers_post, cookies=auth_cookies, data=data)
        except requests.exceptions.ConnectionError:
            raise BadConnectionError('Плохое соединение с интернетом')

        self.__check_draft_creation(response.text)

    def __define_app_type(self, url):
        if 'EF' in url:
            return 'EF'
        if 'ZK' in url:
            return 'ZK'
        if 'OK' in url:
            return 'OK'

    def __get_app_page(self, app_url, auth_cookies):
        try:
            response = requests.get(app_url, headers=self.headers_get, cookies=auth_cookies)
        except requests.exceptions.ConnectionError:
            raise BadConnectionError('Плохое соединение с интернетом')
        if response.status_code != 200:
            raise BadResponseError(f'Не удалось открыть страницу заявки! Код {response.status_code}')
        return response.text

    def __parse_app_page(self, source_html):
        dom = html.fromstring(source_html)
        self.source_data['event_target'] = dom.xpath('//input[@id = "__EVENTTARGET"]/@value')[0]
        self.source_data['event_argument'] = dom.xpath('//input[@id = "__EVENTARGUMENT"]/@value')[0]

        view_state_count = ''.join(dom.xpath('//input[@id = "__VIEWSTATEFIELDCOUNT"]/@value'))
        self.source_data['view_state_count'] = int(view_state_count) if view_state_count else 1
        self.source_data[f'view_state'] = dom.xpath('//input[@id = "__VIEWSTATE"]/@value')[0]
        for i in range(1, self.source_data['view_state_count']):
            self.source_data[f'view_state_{i}'] = dom.xpath(f'//input[@id = "__VIEWSTATE{i}"]/@value')[0]

        self.source_data['view_state_generator'] = dom.xpath('//input[@id = "__VIEWSTATEGENERATOR"]/@value')[0]
        self.source_data['xml_data'] = dom.xpath('//input[@id = "ctl00_ctl00_phWorkZone_xmlData"]/@value')[0]

        self.source_data['user_fio'] = ''.join(dom.xpath('//input[@name = "user_fio"]/@value'))
        self.source_data['user_phone'] = ''.join(dom.xpath('//input[@name = "user_phone"]/@value'))
        self.source_data['user_email'] = ''.join(dom.xpath('//input[@name = "user_email"]/@value'))
        self.source_data['selected_provider'] = ''.join(dom.xpath('//input[@id = "ctl00_ctl00_phWorkZone_SignPanel_selectedProvider"]/@value'))

    def __parse_app_xml(self, source_xml, app_type):
        xml = html.fromstring(source_xml)
        self.data_for_xml['purch_id'] = xml.xpath('//purchid/text()')[0]
        self.data_for_xml['short_name'] = xml.xpath('//shortname/text()')[0]
        self.data_for_xml['purch_code'] = xml.xpath('//purchcode/text()')[0]
        self.data_for_xml['purch_type'] = xml.xpath('//purchtype/text()')[0]
        self.data_for_xml['purch_name'] = xml.xpath('//purchname/text()')[0]
        self.data_for_xml['public_date'] = xml.xpath('//publicdate/text()')[0]
        self.data_for_xml['request_date'] = xml.xpath('//requestdate/text()')[0]
        self.data_for_xml['org_name'] = xml.xpath('//orgname/text()')[0]
        self.data_for_xml['purch_amount'] = xml.xpath('//purchamount/text()')[0]
        self.data_for_xml['purch_descriptions'] = html.tostring(xml.xpath('//purchdescriptions')[0], encoding='unicode')  # ???
        self.data_for_xml['currency'] = xml.xpath('//currency/text()')[0]
        self.data_for_xml['supp_buid'] = xml.xpath('//suppbuid/text()')[0]
        self.data_for_xml['req_supp_name'] = xml.xpath('//reqsuppname/text()')[0]
        self.data_for_xml['person_full_name'] = xml.xpath('//personfullname/text()')[0]
        self.data_for_xml['req_supp_fact_address'] = xml.xpath('//reqsuppfactaddress/text()')[0]
        self.data_for_xml['can_edit_address'] = xml.xpath('//caneditaddress/text()')[0]
        self.data_for_xml['req_supp_post_address'] = xml.xpath('//reqsupppostaddress/text()')[0]
        self.data_for_xml['req_supp_phone'] = xml.xpath('//reqsuppphone/text()')[0]
        self.data_for_xml['supp_inn'] = xml.xpath('//suppinn/text()')[0]
        self.data_for_xml['supp_kpp'] = xml.xpath('//suppkpp/text()')[0]
        self.data_for_xml['supp_type'] = xml.xpath('//supptype/text()')[0]
        self.data_for_xml['supp_max_contract_amount'] = xml.xpath('//suppmaxcontractamount/text()')[0]
        self.data_for_xml['template_create_date'] = xml.xpath('//templatecreatedate/text()')[0]
        self.data_for_xml['placing_way_code'] = xml.xpath('//placingwaycode/text()')[0]

        if app_type == 'EF':
            self.data_for_xml['purch_version'] = xml.xpath('//purchversion/text()')[0]
            self.data_for_xml['purch_cover_amount'] = xml.xpath('//purchcoveramount/text()')[0]
            self.data_for_xml['notification_features'] = html.tostring(xml.xpath('//notificationfeatures')[0], encoding='unicode')  # ???
        elif app_type == 'ZK':
            self.data_for_xml['preferences'] = html.tostring(xml.xpath('//preferences')[0], encoding='unicode')  # ???
            self.data_for_xml['bu_email'] = xml.xpath('//buemail/text()')[0]
        elif app_type == 'OK':
            self.data_for_xml['show_price_offer_file'] = xml.xpath('//showpriceofferfile/text()')[0]
            self.data_for_xml['is_purch_cost_details'] = xml.xpath('//ispurchcostdetails/text()')[0]
            self.data_for_xml['purch_cover_amount'] = xml.xpath('//purchcoveramount/text()')[0]
            self.data_for_xml['preferences'] = html.tostring(xml.xpath('//preferences')[0], encoding='unicode')  # ???

    def __generate_creating_draft_form_data(self, app_type):
        data = dict()
        data['__EVENTTARGET'] = self.source_data['event_target']
        data['__EVENTARGUMENT'] = self.source_data['event_argument']
        data['__VIEWSTATE'] = self.source_data['view_state']

        data['__VIEWSTATEFIELDCOUNT'] = self.source_data['view_state_count']
        for i in range(1, self.source_data['view_state_count']):
            data[f'__VIEWSTATE{i}'] = self.source_data[f'view_state_{i}']

        data['__VIEWSTATEGENERATOR'] = self.source_data['view_state_generator']
        data['__SCROLLPOSITIONX'] = 0
        data['__SCROLLPOSITIONY'] = 0
        data['ctl00$ctl00$phWorkZone$xmlData'] = self.__generate_xml(app_type)
        data['ctl00$ctl00$phWorkZone$signLog'] = ''
        data['ctl00$ctl00$phWorkZone$signValue'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$placingWayCode'] = self.data_for_xml['placing_way_code']
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$bxAccount$account'] = '' # вроде работает и без него
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqAgreement'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$ProductCountry$countryname'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$signType'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$spFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$ctlHash'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$ctlSign'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$signed'] = 'True'
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$SourceFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDocsPart1$ctlHash2012'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$suppBuID'] = self.data_for_xml['supp_buid']
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$ctl00'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$ctl01'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDeclarationRequirements'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$reqDeclarationSMP'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$signType'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$spFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$ctlHash'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$ctlSign'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$signed'] = 'True'
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$SourceFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$preferenceDocs$ctlHash2012'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$signType'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$spFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$ctlHash'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$ctlSign'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$signed'] = 'True'
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$SourceFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttach2$ctlHash2012'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttachAndAmount1$signType'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttachAndAmount1$spFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttachAndAmount1$ctlHash'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttachAndAmount1$ctlSign'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$FileAttachAndAmount1$SourceFileID'] = ''
        data['ctl00$ctl00$phWorkZone$phDocumentZone$nbtPurchaseRequest$iptClientInfo'] = 'Browser name: Chrome; Browser version: 95; OS: Windows'
        data['user_fio'] = self.source_data['user_fio']
        data['user_phone'] = self.source_data['user_phone']
        data['user_email'] = self.source_data['user_email']
        data['ctl00$ctl00$phWorkZone$SignPanel$selectedCertHash'] = ''
        data['ctl00$ctl00$phWorkZone$SignPanel$selectedProvider'] = self.source_data['selected_provider']
        data['ctl00$ctl00$phWorkZone$btnSaveDraft'] = 'Сохранить как черновик'
        data['ctl00$ctl00$phWorkZone$xmlContainerForPreview'] = ''
        return data

    def __generate_xml(self, app_type):
        app = ApplicationXML(self.xml_templates_paths[app_type])
        app.add_fields(
            purch_id=self.data_for_xml['purch_id'],
            short_name=self.data_for_xml['short_name'],
            purch_code=self.data_for_xml['purch_code'],
            purch_type=self.data_for_xml['purch_type'],
            purch_name=self.data_for_xml['purch_name'],
            public_date=self.data_for_xml['public_date'],
            request_date=self.data_for_xml['request_date'],
            org_name=self.data_for_xml['org_name'],
            purch_amount=self.data_for_xml['purch_amount'],
            purch_descriptions=self.data_for_xml['purch_descriptions'],
            currency=self.data_for_xml['currency'],
            supp_buid=self.data_for_xml['supp_buid'],
            req_supp_name=self.data_for_xml['req_supp_name'],
            person_full_name=self.data_for_xml['person_full_name'],
            req_supp_fact_address=self.data_for_xml['req_supp_fact_address'],
            can_edit_address=self.data_for_xml['can_edit_address'],
            req_supp_post_address=self.data_for_xml['req_supp_post_address'],
            req_supp_phone=self.data_for_xml['req_supp_phone'],
            supp_inn=self.data_for_xml['supp_inn'],
            supp_kpp=self.data_for_xml['supp_kpp'],
            supp_type=self.data_for_xml['supp_type'],
            supp_max_contract_amount=self.data_for_xml['supp_max_contract_amount'],
            template_create_date=self.data_for_xml['template_create_date'],
            placing_way_code=self.data_for_xml['placing_way_code'],
            user_fio=self.source_data['user_fio'],
            user_phone=self.source_data['user_phone'],
            user_email=self.source_data['user_email']
        )

        if app_type == 'EF':
            app.add_fields(
                purch_cover_amount=self.data_for_xml['purch_cover_amount'],
                purch_version=self.data_for_xml['purch_version'],
                notification_features=self.data_for_xml['notification_features']
            )
        elif app_type == 'ZK':
            app.add_fields(
                preferences=self.data_for_xml['preferences'],
                bu_email=self.data_for_xml['bu_email']
            )
        elif app_type == 'OK':
            app.add_fields(
                show_price_offer_file=self.data_for_xml['show_price_offer_file'],
                is_purch_cost_details=self.data_for_xml['is_purch_cost_details'],
                purch_cover_amount=self.data_for_xml['purch_cover_amount'],
                preferences=self.data_for_xml['preferences']
            )

        xml = app.fill_template()
        return xml.replace('\n', '')

    def __check_draft_creation(self, source_html):
        dom = html.fromstring(source_html)
        success_msg = ''.join(dom.xpath('//span[@id = "ctl00_ctl00_phWorkZone_successMsg"]/text()'))
        if not success_msg:
            raise CreatingDraftError('Сообщение об успешном создании не найдено')
        return success_msg

# Открытие черновика -------------------------------------------------------------------------------------------------

    def open_draft(self, driver, number, auth_cookies):
        try:
            source_html = self.__get_drafts_page(auth_cookies)
            url = self.__get_draft_url(source_html, number)
            self.__open_draft_page(driver, url)
        except Exception as ex:
            raise Exception(f'Ошибка при открытии черновика:\n{ex}')

    def __get_draft_url(self, source_html, number):
        dom = html.fromstring(source_html)
        xml = dom.xpath('//textarea[@id = "ctl00_ctl00_phWorkZone_xmlData"]/text()')[0]
        xml_dom = html.fromstring(xml)
        try:
            url = self.main_url + xml_dom.xpath(f'//purchcode[text() = "{number}"]/..//dckviewform/text()')[0]
        except:
            raise Exception(f'Черновика с номером {number} не существует!')
        return url

    def __open_draft_page(self, driver, url):
        driver.get(url)

# Удаление черновиков ------------------------------------------------------------------------------------------------

    def delete_all_drafts(self, auth_cookies):
        try:
            source_html = self.__get_drafts_page(auth_cookies)
            source_data = self.__parse_drafts_page(source_html)
            xml_data = self.__parse_drafts_xml(source_data['xml_data'])
            form_data = self.__generate_deleting_drafts_form_data(source_data, xml_data)
            response = requests.post(self.drafts_page_url, headers=self.headers_post, cookies=auth_cookies, data=form_data)
        except Exception as ex:
            raise Exception(f'Ошибка при удалении черновиков:\n{ex}')
        return response.text

    def __get_drafts_page(self, auth_cookies):
        response = requests.get(self.drafts_page_url, headers=self.headers_get, cookies=auth_cookies)
        if response.status_code != 200:
            raise Exception('Не удалось открыть страницу с черновиками!')
        return response.text

    def __parse_drafts_page(self, source_html):
        dom = html.fromstring(source_html)
        source_data = dict()
        source_data['event_target'] = dom.xpath('//input[@id = "__EVENTTARGET"]/@value')[0]
        source_data['event_argument'] = dom.xpath('//input[@id = "__EVENTARGUMENT"]/@value')[0]
        source_data['view_state'] = dom.xpath('//input[@id = "__VIEWSTATE"]/@value')[0]
        source_data['view_state_generator'] = dom.xpath('//input[@id = "__VIEWSTATEGENERATOR"]/@value')[0]
        source_data['xml_data'] = dom.xpath('//textarea[@id = "ctl00_ctl00_phWorkZone_xmlData"]/text()')[0]
        return source_data

    def __parse_drafts_xml(self, source_xml):
        xml = html.fromstring(source_xml)
        xml_data = dict()
        xml_data['ids'] = ','.join(xml.xpath('//id/text()')) + ',undefined'
        return xml_data

    def __generate_deleting_drafts_form_data(self, source_data, xml_data):
        form_data = dict()
        form_data['__EVENTTARGET'] = 'ctl00$ctl00$phWorkZone$phDataZone$ctl00'
        form_data['__EVENTARGUMENT'] = source_data['event_argument']
        form_data['__VIEWSTATE'] = source_data['view_state']
        form_data['__VIEWSTATEGENERATOR'] = source_data['view_state_generator']
        form_data['ctl00$ctl00$phWorkZone$xmlFilter'] = '<query></query>'
        form_data['ctl00$ctl00$phWorkZone$phFilterZone$cldBDate'] = ''
        form_data['ctl00$ctl00$phWorkZone$phFilterZone$purchCode'] = ''
        form_data['ctl00$ctl00$phWorkZone$phFilterZone$orderbyEx'] = 'desc'
        form_data['ctl00$ctl00$phWorkZone$hfFilterZone'] = 'true'
        form_data['ctl00$ctl00$phWorkZone$xmlData'] = source_data['xml_data']
        form_data['ctl00$ctl00$phWorkZone$phDataZone$tborderbyEx'] = 'desc'
        form_data['ctl00$ctl00$phWorkZone$phDataZone$hdnDelete'] = xml_data['ids']
        return form_data


class ApplicationXML:
    def __init__(self, template_path):
        self.template_path = template_path
        self.template = self.__load_template()
        self.fields = dict()

    def __load_template(self):
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return template

    def add_fields(self, **args):
        self.fields.update(args)

    def fill_template(self):
        return self.template.format(**self.fields)

# -------------------------------------------------------------------------------------------


class Api(api_patterns.MainApiPattern):
    def __init__(self):
        super().__init__(AuthorizationApi(), ParsingApi(), AppsSendingApi())
