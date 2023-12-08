import shutil
import pandas as pd

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QFileDialog, \
    QMessageBox, QTableView, QInputDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
import sys
import uuid
from datetime import datetime
import os





class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()

        self.db_name = ''
        self.table_name = ''
        self.connection = None

        self.create_db_button = QPushButton('➕📄 Создать Базу Данных', self)
        self.open_db_table_button = QPushButton('📂 Открыть Базу Данных и таблицу', self)
        self.add_data_button = QPushButton('➕ Добавить данные', self)
        self.delete_data_button = QPushButton('🗑 Удалить записи', self)
        self.search_data_button = QPushButton('🔎 Поиск по значению', self)
        self.edit_data_button = QPushButton('✏ Редактировать запись', self)
        self.delete_db_button = QPushButton('❌ Удалить БД', self)
        self.clear_table_button = QPushButton('🆑 Очистить таблицу', self)
        self.backup_button = QPushButton('🙂 Создать Backup', self)
        self.restore_button = QPushButton('🤨 Восстановить из Backup', self)
        self.save_button = QPushButton('😴 Сохранить в файл', self)

        self.search_result_window = None

        self.create_db_button.clicked.connect(self.create_database)
        self.open_db_table_button.clicked.connect(self.open_database_and_table)
        self.add_data_button.clicked.connect(self.show_data_form)
        self.delete_data_button.clicked.connect(self.delete_data)
        self.search_data_button.clicked.connect(self.search_data)
        self.edit_data_button.clicked.connect(self.edit_data)
        self.delete_db_button.clicked.connect(self.delete_database)
        self.clear_table_button.clicked.connect(self.clear_table)
        self.backup_button.clicked.connect(self.create_backup)
        self.restore_button.clicked.connect(self.restore_backup)
        self.save_button.clicked.connect(self.save_database)


        self.add_data_button.setEnabled(False)
        self.delete_data_button.setEnabled(False)
        self.search_data_button.setEnabled(False)
        self.edit_data_button.setEnabled(False)
        self.delete_db_button.setEnabled(False)
        self.clear_table_button.setEnabled(False)
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.save_button.setEnabled(False)



        layout = QVBoxLayout()
        layout.addWidget(self.create_db_button)
        layout.addWidget(self.open_db_table_button)
        layout.addWidget(self.add_data_button)
        layout.addWidget(self.delete_data_button)
        layout.addWidget(self.search_data_button)
        layout.addWidget(self.edit_data_button)
        layout.addWidget(self.delete_db_button)
        layout.addWidget(self.clear_table_button)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.restore_button)
        layout.addWidget(self.save_button)


        self.setLayout(layout)
    def clear_table(self):
        if not self.db_name:
            return

        query = QSqlQuery(self.connection)

        # Очищаем все значения в таблице
        if query.prepare(f"DELETE FROM {self.table_name}"):
            if not query.exec_():
                print("Ошибка очистки таблицы:", query.lastError().text())
            else:
                print("Таблица успешно очищена")

            query.finish()


    def create_database(self):
        db_name, ok_pressed = QFileDialog.getSaveFileName(self, 'Создать Базу Данных', "", "SQLite Database Files (*.db);;All Files (*)")
        if ok_pressed and db_name:
            self.db_name = db_name

            default_table_name = "Table_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            table_name, ok_pressed = QInputDialog.getText(self, 'Введите имя таблицы', 'Имя таблицы:', QLineEdit.Normal, default_table_name)
            if ok_pressed and table_name:
                self.table_name = table_name

                self.connection = QSqlDatabase.addDatabase("QSQLITE", str(uuid.uuid4()))
                self.connection.setDatabaseName(self.db_name)

                if not self.connection.open():
                    print("Ошибка открытия базы данных")
                    return

                query = QSqlQuery(self.connection)
                query.exec(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER PRIMARY KEY UNIQUE, name TEXT, age INTEGER, city TEXT)")

                self.connection.close()

                self.add_data_button.setEnabled(True)
                self.delete_data_button.setEnabled(True)
                self.search_data_button.setEnabled(True)
                self.edit_data_button.setEnabled(True)
                self.delete_db_button.setEnabled(True)
                self.clear_table_button.setEnabled(True)
                self.backup_button.setEnabled(True)
                self.restore_button.setEnabled(True)
                self.save_button.setEnabled(True)

    def save_database(self):
        if not self.db_name:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, 'Выберите место для сохранения файла', '',
                                                   'Excel Files (*.xlsx);;DB files (*.db);;CSV Files (*.csv)')

        if file_path:
            try:
                # Загружаем данные из базы данных в DataFrame
                query = QSqlQuery(self.connection)
                query.prepare(f"SELECT * FROM {self.table_name}")
                if not query.exec_():
                    print("Ошибка чтения данных:", query.lastError().text())
                    return

                data = []
                while query.next():
                    record = query.record()
                    row_data = [record.value('id'), record.value('name'), record.value('age'),
                                record.value('city')]
                    data.append(row_data)

                columns = ['id', 'name', 'age', 'city']
                df = pd.DataFrame(data, columns=columns)

                # Сохраняем DataFrame в выбранный файл
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                elif file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False)
                else:
                    print("Выбран неизвестный формат файла")
                    return

                print(f"Данные успешно сохранены в файл: {file_path}")
            except Exception as e:
                print(f"Ошибка при сохранении данных: {str(e)}")

    def create_backup(self):
        if not self.db_name:
            return

        backup_path, _ = QFileDialog.getSaveFileName(self, 'Выберите место сохранения backup-файла', '',
                                                     'Backup Files (*.bak)')

        if backup_path:
            try:
                # Копируем текущий файл базы данных в backup-файл
                shutil.copy(self.db_name, backup_path)
                print(f"Backup-файл успешно создан: {backup_path}")
            except Exception as e:
                print(f"Ошибка при создании backup-файла: {str(e)}")

    def restore_backup(self):
        if not self.db_name:
            return

        backup_path, _ = QFileDialog.getOpenFileName(self, 'Выберите backup-файл для восстановления', '',
                                                     'Backup Files (*.bak)')

        if backup_path:
            try:
                # Копируем backup-файл в текущий файл базы данных
                shutil.copy(backup_path, self.db_name)
                print("База данных успешно восстановлена из backup-файла")
            except Exception as e:
                print(f"Ошибка при восстановлении из backup-файла: {str(e)}")
    def open_database_and_table(self):
        db_name, _ = QFileDialog.getOpenFileName(self, "Открыть Базу Данных", "", "SQLite Database Files (*.db);;All Files (*)")
        if db_name:
            self.db_name = db_name

            self.connection = QSqlDatabase.addDatabase("QSQLITE", str(uuid.uuid4()))
            self.connection.setDatabaseName(self.db_name)

            if not self.connection.open():
                print("Ошибка открытия базы данных")
                return

            tables = self.connection.tables()
            if tables:
                table_name, ok_pressed = QInputDialog.getItem(self, 'Выберите таблицу', 'Таблицы:', tables, 0, False)
                if ok_pressed:
                    self.table_name = table_name
                    self.add_data_button.setEnabled(True)
                    self.delete_data_button.setEnabled(True)
                    self.search_data_button.setEnabled(True)
                    self.edit_data_button.setEnabled(True)
                    self.delete_db_button.setEnabled(True)
                    self.clear_table_button.setEnabled(True)
                    self.backup_button.setEnabled(True)
                    self.restore_button.setEnabled(True)
                    self.save_button.setEnabled(True)
                    self.open_table()
            else:
                print("В выбранной базе данных нет таблиц")

    def open_table(self):
        if not self.db_name:
            return



    def show_data_form(self):
        if not self.db_name:
            return

        data_form = DataForm(self.db_name, self.table_name, self.connection, self)
        data_form.exec_()

    def delete_data(self):
        if not self.db_name or not self.table_name:
            return

        value, ok_pressed = QInputDialog.getText(self, 'Удаление данных', 'Введите значение для удаления:',
                                                 QLineEdit.Normal, '')
        if ok_pressed:
            query = QSqlQuery(self.connection)

            query.prepare(f"DELETE FROM {self.table_name} WHERE id = :value")
            query.bindValue(":value", value)

            if not query.exec_():
                print("Ошибка удаления данных:", query.lastError().text())



            query.finish()  # Завершаем выполнение запроса

            for field in ["name", "age", "city"]:
                query.prepare(
                    f"UPDATE {self.table_name} SET {field} = NULL WHERE {field} = :value AND id <> :value")
                query.bindValue(":value", value)
                query.bindValue(":key_value", value)

                if not query.exec_():
                    print(f"Ошибка удаления данных из поля {field}:", query.lastError().text())
                query.finish()
    def search_data(self):
        if not self.db_name or not self.table_name:
            return

        value, ok_pressed = QInputDialog.getText(self, 'Поиск данных', 'Введите значение для поиска:', QLineEdit.Normal,
                                                 '')
        if ok_pressed:
            query = QSqlQuery(self.connection)

            query.prepare(
                f"SELECT * FROM {self.table_name} WHERE id LIKE :value OR name LIKE :value OR age LIKE :value OR city LIKE :value")
            query.bindValue(":value", f"%{value}%")

            if not query.exec_():
                print("Ошибка выполнения запроса:", query.lastError().text())
            else:
                search_result = []
                while query.next():
                    record = query.record()
                    result = f"id: {record.value('id')}, name: {record.value('name')}, age: {record.value('age')}, city: {record.value('city')}"
                    search_result.append(result)

                if search_result:
                    self.show_search_result(search_result)  # Показываем окно с результатами
                else:
                    QMessageBox.information(self, 'Поиск данных', 'Ничего не найдено.')

                query.finish()  # Завершаем выполнение запроса

    def show_search_result(self, search_result):
        if not self.search_result_window:
            self.search_result_window = SearchResultWindow(search_result)
            self.search_result_window.show()
        else:
            self.search_result_window.update_results(search_result)

    def edit_data(self):
        if not self.db_name or not self.table_name:
            return

        key_field_name = 'id'  # Имя ключевого поля
        current_key, ok_pressed = QInputDialog.getText(self, 'Редактирование данных',
                                                       f'Введите текущее значение id ({key_field_name}):',
                                                       QLineEdit.Normal, '')
        if not ok_pressed:
            return

        new_key, ok_pressed = QInputDialog.getText(self, 'Редактирование данных',
                                                   f'Введите новое значение id ({key_field_name}):',
                                                   QLineEdit.Normal, '')
        if not ok_pressed:
            return

        new_field2_value, ok_pressed = QInputDialog.getText(self, 'Редактирование данных',
                                                            'Введите новое значение name:', QLineEdit.Normal, '')
        if not ok_pressed:
            return

        new_field3_value, ok_pressed = QInputDialog.getText(self, 'Редактирование данных',
                                                            'Введите новое значение age:', QLineEdit.Normal, '')
        if not ok_pressed:
            return

        new_field4_value, ok_pressed = QInputDialog.getText(self, 'Редактирование данных',
                                                            'Введите новое значение city:', QLineEdit.Normal, '')
        if not ok_pressed:
            return

        query = QSqlQuery(self.connection)
        query.prepare(
            f"UPDATE {self.table_name} SET field1 = :new_key, field2 = :new_field2, field3 = :new_field3, field4 = :new_field4 WHERE field1 = :current_key")
        query.bindValue(":new_key", new_key)
        query.bindValue(":new_field2", new_field2_value)
        query.bindValue(":new_field3", new_field3_value)
        query.bindValue(":new_field4", new_field4_value)
        query.bindValue(":current_key", current_key)

        if not query.exec_():
            print("Ошибка редактирования данных:", query.lastError().text())
        else:
            print("Данные отредактированы успешно")

    def delete_database(self):
        reply = QMessageBox.question(self, 'Удаление БД', 'Вы уверены, что хотите удалить БД?\nЭто действие нельзя отменить.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.connection:
                self.connection.close()

            if os.path.exists(self.db_name):
                os.remove(self.db_name)

            self.db_name = ''
            self.table_name = ''
            self.add_data_button.setEnabled(False)
            self.delete_data_button.setEnabled(False)
            self.search_data_button.setEnabled(False)
            self.edit_data_button.setEnabled(False)
            self.delete_db_button.setEnabled(False)
class SearchResultWindow(QDialog):
    def __init__(self, initial_results, parent=None):
        super(SearchResultWindow, self).__init__(parent)
        self.results_layout = QVBoxLayout()
        self.setLayout(self.results_layout)
        self.update_results(initial_results)

    def update_results(self, results):
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for result in results:
            label = QLabel(result)
            self.results_layout.addWidget(label)
class DataForm(QDialog):
    def __init__(self, db_name, table_name, connection, parent):
        super().__init__(parent)

        self.db_name = db_name
        self.table_name = table_name
        self.connection = connection

        self.field1_edit = QLineEdit(self)
        self.field2_edit = QLineEdit(self)
        self.field3_edit = QLineEdit(self)
        self.field4_edit = QLineEdit(self)

        add_data_button = QPushButton('Добавить данные', self)
        add_data_button.clicked.connect(self.add_data)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('ID (ключевое, уникальное):'))
        layout.addWidget(self.field1_edit)
        layout.addWidget(QLabel('Name:'))
        layout.addWidget(self.field2_edit)
        layout.addWidget(QLabel('Age:'))
        layout.addWidget(self.field3_edit)
        layout.addWidget(QLabel('City:'))
        layout.addWidget(self.field4_edit)
        layout.addWidget(add_data_button)

        self.setLayout(layout)

    def add_data(self):
        if not self.connection or not self.connection.isValid() or not self.connection.open():
            print("Ошибка открытия базы данных")
            return

        query = QSqlQuery(self.connection)
        query.prepare(f"INSERT INTO {self.table_name} (id, name, age, city) VALUES (:id, :name, :age, :city)")
        query.bindValue(":id", self.field1_edit.text())
        query.bindValue(":name", self.field2_edit.text())
        query.bindValue(":age", self.field3_edit.text())
        query.bindValue(":city", self.field4_edit.text())

        if not query.exec_():
            error_message = query.lastError().text()
            if "UNIQUE constraint failed" in error_message:
                QMessageBox.critical(self, "Ошибка уникальности", "Запись с таким ключом уже существует.")
            else:
                print("Ошибка добавления данных:", error_message)
        else:
            print("Данные добавлены успешно")

        self.accept()

class TableDialog(QDialog):
    def __init__(self, db_name, table_name, connection):
        super().__init__()

        self.db_name = db_name
        self.table_name = table_name
        self.connection = connection

        self.table_model = QSqlTableModel()
        self.table_model.setTable(self.table_name)
        self.table_model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.table_model.select()

        table_view = QTableView(self)
        table_view.setModel(self.table_model)

        delete_record_button = QPushButton('Удалить запись', self)
        delete_record_button.clicked.connect(self.delete_selected_record)

        layout = QVBoxLayout()
        layout.addWidget(table_view)
        layout.addWidget(delete_record_button)
        self.setLayout(layout)

    def delete_selected_record(self, table_view=None):
        selected_indexes = table_view.selectionModel().selectedIndexes()
        if selected_indexes:
            for index in selected_indexes:
                row = index.row()
                self.table_model.removeRow(row)
                self.table_model.submitAll()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = DatabaseApp()
    main_app.show()
    sys.exit(app.exec_())
