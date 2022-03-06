import json
from qgis.PyQt.QtWidgets import QTableWidgetItem


class DataRow(dict):
    def __init__(self, column_list, column_defn):
        super(DataRow, self).__init__()
        self._column_list = column_list
        self._column_defn = column_defn

        self._populate_default_value()

    def _populate_default_value(self):
        for col in self._column_list:
            val = self._column_defn[col]
            self[col] = val

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self._column_list[key]

        super().__setitem__(key, value)

    def __getitem__(self, key):
        if isinstance(key, int):
            key = self._column_list[key]
        return super().__getitem__(key)


class DataTable:
    def __init__(self):
        self._rows = []
        self._column_list = []
        self._column_defn = {}
        self._hidden_column = {}
        self._table_widget = {}

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._column_list

    def add_column(self, name, default_value=None):
        if name in self._column_defn:
            raise KeyError("Column already exists")
        self._column_list.append(name)
        self._column_defn[name] = default_value

    def new_row(self):
        row = DataRow(self._column_list, self._column_defn)
        self._rows.append(row)
        return row

    @property
    def rows(self):
        return self._rows

    def render_to_qtable_widget(self, table_widget, hidden_index=[]):
        table_widget.setRowCount(0)
        uid = hex(id(table_widget))
        self._table_widget[uid] = table_widget
        self._hidden_column[uid] = hidden_index

        if not self._rows:
            return

        columns = self.columns
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels(columns)

        for row in self._rows:
            pos = table_widget.rowCount()
            table_widget.insertRow(pos)

            for index, col in enumerate(columns):
                table_widget.setItem(pos, index, QTableWidgetItem(str(row[col])))

        for index in hidden_index:
            table_widget.setColumnHidden(index, True)

    def _get_table_widget_uid(self, table_widget=None):
        if not table_widget:
            uid = list(self._table_widget.keys()).pop()
        else:
            uid = hex(id(table_widget))
        return uid

    def _get_hidden_columns(self, table_widget=None):
        uid = self._get_table_widget_uid(table_widget)
        if not uid or uid not in self._hidden_column:
            raise KeyError(f"table widget with uid: {uid} not found!")

        hidden_index = self._hidden_column[uid]
        return hidden_index

    def reload_qtable_widget(self, table_widget=None):
        hidden_index = self._get_hidden_columns(table_widget)
        self.render_to_qtable_widget(table_widget, hidden_index)

    def get_selected_qtable_widget(self, table_widget=None, raw=False):
        uid = self._get_table_widget_uid(table_widget)
        hidden_index = self._get_hidden_columns(table_widget)

        if raw:
            index = self._table_widget[uid].currentRow()
            return self._rows[index]
        else:
            for index in hidden_index:
                self._table_widget[uid].setColumnHidden(index, False)

            selected = self._table_widget[uid].selectedItems()

            for index in hidden_index:
                self._table_widget[uid].setColumnHidden(index, True)

            return selected


class Dataset(dict):
    def __init__(self, data={}):
        super(Dataset, self).__init__()
        self._data = {}

        if data:
            self.load_data(data)

    def add_table(self, name):
        if name in self:
            raise KeyError("Table is already exists")

        data = DataTable()
        self._data[name] = data
        self[name] = data
        return data

    def load_data(self, data, merge_dfn=True):
        if isinstance(data, str):
            data = json.loads(data)
        if isinstance(data, bytes):
            data = json.loads(data.decode("utf-8"))

        self.from_dict(data, merge_dfn)

    def from_dict(self, data, merge_dfn=True):
        for table_name, rows in data.items():
            if not merge_dfn and table_name not in self:
                raise KeyError(f"Table {table_name} is not exists")

            if not isinstance(rows, list):
                raise ValueError("Not a table")

            table = (
                self[table_name] if table_name in self else self.add_table(table_name)
            )

            if not rows:
                continue

            for col in rows[0]:
                table.add_column(col)
            for row in rows:
                new_row = table.new_row()
                for col_name, value in row.items():
                    new_row[col_name] = value

    def get_selected_qtable_widget(self, table_name, table_widget=None):
        if table_name not in self._data:
            raise KeyError(f"Table {table_name} is not exists")
        data = self._data[table_name]
        selected = data.get_selected_qtable_widget(table_widget)
        return selected

    def render_to_qtable_widget(self, table_name, table_widget, hidden_index=[]):
        if table_name not in self._data:
            raise KeyError(f"Table {table_name} is not exists")
        data = self._data[table_name]
        data.render_to_qtable_widget(table_widget, hidden_index)

    def to_json(self):
        result = {}
        for table, value in self._data.items():
            result[table] = value.rows
        return result
