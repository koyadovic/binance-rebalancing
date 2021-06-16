from core.domain.interfaces import AbstractUserInterface
from texttable import Texttable


class TextUserInterface(AbstractUserInterface):
    def show_rebalance_summary(self, summary: list, total_balance: str):
        table = Texttable()
        table.set_cols_align(["c", "c", "c", "c", "c", "c"])
        table_rows = [[
                          'Asset',
                          'Wanted amount',
                          'Wanted %',
                          'Current amount',
                          'Current %',
                          'Action'
                      ]] + summary

        # Printing summary and asking for rebalancing
        table.add_rows(table_rows)
        print(table.draw() + '\n')
        print(f'TOTAL BALANCE: {total_balance}')

    def request_confirmation(self, text: str) -> bool:
        print(text)
        response = input('(y/n) ').lower().strip()
        return response == 'y'

    def show_message(self, text: str):
        print(text)
