from core.domain.interfaces import AbstractUserInterface
from texttable import Texttable


def capitalize(string):
    return string[0].upper() + string[1:]


class TextUserInterface(AbstractUserInterface):
    def show_table(self, headers: list, rows: list, **additional_data):
        table = Texttable()
        table.set_cols_align(['c'] * len(headers))
        table_rows = [headers] + rows
        table.add_rows(table_rows)
        print(table.draw() + '\n')
        for k, v in additional_data.items():
            print(f'{capitalize(k.replace("_", " "))}: {v}')

    def request_confirmation(self, text: str) -> bool:
        print(text)
        response = input('(y/n) ').lower().strip()
        return response == 'y'

    def show_message(self, text: str):
        print(text)
