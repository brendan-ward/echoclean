from collections import OrderedDict
from openpyxl import load_workbook, Workbook


class DictReader(object):
    def __init__(self, worksheet):
        self.fieldnames = []
        column_idx = []
        row_iter = worksheet.iter_rows()

        for cell in row_iter.next():
            if not cell.value:  # Any blank column is beyond range of data
                break
            self.fieldnames.append(cell.value)
            column_idx.append(cell.column)

        self.column_range = (column_idx[0], column_idx[-1])

        # Setup rows iter
        self.data_range = '{0}2:{1}{2}'.format(
            self.column_range[0],
            self.column_range[1],
            worksheet.get_highest_row()
        )
        self._iter_rows = worksheet.iter_rows(self.data_range)

    def __iter__(self):
        return self

    def next(self):
        row = self._iter_rows.next()
        return OrderedDict([(k, v) for k, v in zip(self.fieldnames, [r.value for r in row])])

    @classmethod
    def from_file(cls, filename, index=None):
        """Read sheet from filename
        If index is not specified, the active sheet will be used.
        """

        workbook = load_workbook(filename, data_only=True, guess_types=True)
        worksheet = workbook.sheets[index] if index is not None else workbook.active
        return cls(worksheet)