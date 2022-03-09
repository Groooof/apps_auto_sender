import sqlite3
from .config import WindowConfig
from .observer_pattern import Subject


class DB:
    def __init__(self, table_name, db_path):
        self.path = db_path
        self.table = table_name
        self.sorting_orders = {'a_z': 'ASC',
                               'z_a': 'DESC'}
        self.fields = ('name', 'number', 'price', 'public_date', 'request_date', 'request_accept_date', 'auction_begin_date', 'requested', 'public_date_time', 'url')
        self.__connect()

    def create_table(self):
        cursor = self.connection
        query = f''' CREATE TABLE IF NOT EXISTS {self.table}(
        name TEXT, 
        number TEXT UNIQUE, 
        price TEXT, 
        public_date TEXT,
        request_date TEXT, 
        request_accept_date TEXT,
        auction_begin_date TEXT, 
        requested TEXT, 
        public_date_time INTEGER
        ) '''
        cursor.execute(query)
        #self.__disconnect()

    def select(self, condition='', sort='a_z'):
        cursor = self.connection
        condition = ' WHERE ' + condition + ' ' if condition else ''
        query = f''' SELECT * FROM {self.table}{condition} ORDER BY public_date_time {self.sorting_orders[sort]} '''
        records = cursor.execute(query).fetchall()
        self.connection.commit()
        #self.__disconnect()
        return records

    def insert_or_ignore(self, records):
        cursor = self.connection
        query = f''' INSERT OR IGNORE INTO {self.table} ({",".join(self.fields)}) VALUES ({",".join(["?" for i in range(len(self.fields))])});'''
        recorded = cursor.executemany(query, records).rowcount
        self.connection.commit()
        #self.__disconnect()
        return recorded

    def update(self, key, field, new_value):
        cursor = self.connection
        query = f''' UPDATE {self.table} SET {field}={new_value} WHERE number="{key}"'''
        cursor.execute(query)
        self.connection.commit()
        #self.__disconnect()

    def __connect(self):
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        return self.connection.cursor()

    def __disconnect(self):
        #self.connection.commit()
        self.connection.close()

    def __del__(self):
        self.__disconnect()


# -----------------------------------------------------------------------------------------------------------------


class ApplicationsDB(Subject):
    def __init__(self, config: WindowConfig):
        super().__init__()
        self.db = DB(config.DB_TABLE_NAME, config.global_config.db_path)

    def set_checkmark(self, key, value):
        self.db.update(key, 'requested', value)
        data = {
            'from': 'DB',
            'event': 'status',
            'data': {'key': key,
                     'checkmark': value}
        }
        self.notify(data)

    def insert_new_apps(self, records):
        new_records = self.db.insert_or_ignore(records)
        data = {
            'from': 'DB',
            'event': 'insert',
            'data': records
        }
        self.notify(data)
        return new_records

    def get_all_apps(self):
        return self.db.select(sort='a_z')

    def get_last_app(self):
        return self.db.select(sort='z_a')[0]

    def get_unprocessed_apps(self):
        return self.db.select(condition='requested=0', sort='a_z')

    def get_processed_apps(self):
        return self.db.select(condition='requested=1', sort='a_z')
