from tkinter import *
from tkinter.ttk import *
from ..database import ApplicationsDB
from ..observer_pattern import Observer


class OrgNameBlock(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=50, **kwargs)

        self.org_name = StringVar()
        label = Label(self, style='Light.TLabel', textvariable=self.org_name, anchor='w', justify='left')

        label.pack(fill=BOTH, expand=True)
        label.pack_propagate(False)


class TableGUI(Frame):
    def __init__(self, parent, rows=()):
        super().__init__(parent)

        self.org_name_label = OrgNameBlock(self)

        headings = ['Наименование', 'Номер контракта', 'Сумма', 'Опубликовано',
                    'Дата и время окончания \n   срока подачи заявок',
                    'Дата окончания срока \n рассмотрения заявок',
                    'Дата и время проведения \n электронного аукциона', 'Статус ']

        self.table = Treeview(self, show="headings", selectmode="browse")
        self.table["columns"] = headings
        self.table.heading('#0', text='\n\n')
        # self.table.rowconfigure()
        for head in headings:
            self.table.heading(head, text=head, anchor=CENTER)
            self.table.column(head, anchor=CENTER)

        self.table.column('Наименование', width=80)
        self.table.column('Сумма', width=60)
        self.table.column('Номер контракта', width=115)
        self.table.column('Опубликовано', width=100)
        self.table.column('Дата и время окончания \n   срока подачи заявок', width=110)
        self.table.column('Дата окончания срока \n рассмотрения заявок', width=100)
        self.table.column('Дата и время проведения \n электронного аукциона', width=115)
        self.table.column('Статус ', width=30)

        scroll = Scrollbar(self, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.bind('<<TreeviewSelect>>', lambda event: self.on_select())

        self.org_name_label.pack(fill=X)
        self.org_name_label.pack_propagate(False)
        scroll.pack(side=RIGHT, fill=Y)
        self.table.pack(fill=BOTH, expand=True)
        self.pack(fill=X, pady=0, padx=10)

    def on_select(self):
        row_data = self.table.selection()
        name = self.table.item(row_data[0])['values'][0]
        if len(name) > 120:
            words = name.split(' ')
            words_count = len(words)
            for i in range(words_count):
                if len(' '.join(words[:-i - 1])) <= 120:
                    name = ' '.join(words[:-i - 1]) + '\n' + ' '.join(words[-i - 1:])
                    break
        self.org_name_label.org_name.set(name)


class Table(TableGUI):
    def __init__(self, parent):
        super().__init__(parent)

    def __get_records_ids(self):
        return self.table.get_children()

    def __get_table_id_by_number(self, number: str):
        number = str(number).lstrip('0')
        table_record_ids = self.__get_records_ids()
        for table_record_id in table_record_ids:
            table_record_number = self.table.item(table_record_id)['values'][1]
            if str(table_record_number) == str(number):
                return table_record_id
        return 0

    def __get_record_by_table_id(self, table_id):
        return self.table.item(table_id)['values']

    def get_record_by_number(self, number):
        table_id = self.__get_table_id_by_number(number)
        record = self.__get_record_by_table_id(table_id)
        return record

    def insert_record(self, record, pos=0):
        self.table.insert('', index=pos, values=record)

    def insert_or_ignore_record(self, record, pos=0):
        number = record[1]
        table_id = self.__get_table_id_by_number(number)
        if not table_id:
            self.insert_record(record, pos=pos)

    def delete_record(self, record):
        number = record[1]
        table_id = self.__get_table_id_by_number(number)
        if table_id:
            self.table.delete(table_id)
            return 1
        return 0

    def delete_last(self):
        records = self.get_records()
        self.delete_record(records[-1])

    def update_record(self, record):
        # обновляем если существует, иначе - ничего
        number = record[1]
        table_id = self.__get_table_id_by_number(number)
        if table_id:
            self.table.item(table_id, values=record)
            return 1
        return 0

    def upsert_record(self, record, pos=END):
        # обновляем если существует, иначе - добавляем
        if not self.update_record(record):
            self.insert_record(record, pos=pos)

    def get_records_count(self):
        records = self.__get_records_ids()
        return len(records)

    def get_records(self):
        records = []
        table_record_ids = self.__get_records_ids()
        for table_record_id in table_record_ids:
            record = self.__get_record_by_table_id(table_record_id)
            records.append(record)
        return records


# -----------------------------------------------------------------------------------------------------------------


class ApplicationsTable(Observer, Table):
    def __init__(self, parent, db: ApplicationsDB, records_limit=200):
        super().__init__(parent)
        self.records_limit = records_limit
        self.db = db
        self.active = True

    def insert_new_apps(self, records):
        for i, record in enumerate(records):
            self.insert_or_ignore_record(record[:8])
            if self.get_records_count() > self.records_limit:
                self.delete_last()

    def set_checkmark(self, number, value):
        record = self.get_record_by_number(number)
        new_record = (record[0], record[1], record[2], record[3], record[4], record[5], record[6], value)
        self.update_record(new_record)

    def unlock(self):
        self.active = True

    def lock(self):
        self.active = False

    def update(self, data):
        if data['from'] == 'DB' and data['event'] == 'insert' and self.active:
            records = self.db.get_all_apps()
            self.insert_new_apps(records)
        elif data['from'] == 'DB' and data['event'] == 'status' and self.active:
            self.set_checkmark(data['data']['key'], data['data']['checkmark'])
        elif data['from'] == 'Account' and data['event'] == 'log in':
            records = self.db.get_all_apps()
            self.insert_new_apps(records)
            self.unlock()
        elif data['from'] == 'ChildWindow' and data['event'] == 'close':
            self.lock()