import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QStackedWidget, QMessageBox, QTableWidget, QTableWidgetItem,
    QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
import sqlite3

class LoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()

        self.label = QLabel("Введите пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Войти")

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.login_button.clicked.connect(self.check_password)

    def check_password(self):
        if self.password_input.text() == "212223":
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль")

class MainMenuPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()

        self.label = QLabel("Главное меню")
        self.patients_button = QPushButton("Список пациентов")
        self.analyzes_button = QPushButton("Заполнить результаты анализов")
        self.back_button = QPushButton("Назад")

        layout.addWidget(self.label)
        layout.addWidget(self.patients_button)
        layout.addWidget(self.analyzes_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.patients_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.analyzes_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

class PatientsPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        self.label = QLabel("Список пациентов")
        self.patients_list = QLabel()  # Здесь отображается текстовый список пациентов
        self.back_button = QPushButton("Назад")

        layout.addWidget(self.label)
        layout.addWidget(self.patients_list)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.load_patients()

    def load_patients(self):
        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()

        cursor.execute("SELECT name, age, gender, uniqe FROM patients")
        rows = cursor.fetchall()

        if rows:
            patients_text = "\n".join(
                [f"Имя: {row[0]}, Возраст: {row[1]}, Пол: {row[2]}, Уникальный номер: {row[3]}" for row in rows]
            )
            self.patients_list.setText(patients_text)
        else:
            self.patients_list.setText("Пациенты отсутствуют.")

        connection.close()

class AnalyzePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        self.label = QLabel("Заполнить результаты анализов")
        self.form_layout = QFormLayout()
        self.uniqe_input = QLineEdit()
        self.analyze_combobox = QComboBox()
        self.result_combobox = QComboBox()
        self.save_button = QPushButton("Сохранить результаты")
        self.back_button = QPushButton("Назад")

        self.form_layout.addRow("Уникальный номер пациента:", self.uniqe_input)
        self.form_layout.addRow("Вид обследования:", self.analyze_combobox)
        self.form_layout.addRow("Результат:", self.result_combobox)

        self.analyze_combobox.addItems(["Биохимический анализ крови", "Клинический анализ", "Мрт"])
        self.result_combobox.addItems(["Норма", "Не норма", "Не брались"])

        layout.addWidget(self.label)
        layout.addLayout(self.form_layout)
        layout.addWidget(self.save_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.load_analyzes()
        self.save_button.clicked.connect(self.save_result)
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    def load_analyzes(self):
        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM analyzes")
        analyzes = cursor.fetchall()
        self.analyze_combobox.addItems([analyze[0] for analyze in analyzes])

        connection.close()

    def save_result(self):
        uniqe = self.uniqe_input.text()
        analyze = self.analyze_combobox.currentText()
        result = self.result_combobox.currentText()

        if not uniqe:
            QMessageBox.warning(self, "Ошибка", "Введите уникальный номер пациента")
            return

        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO results (uniqe, analyze, result) VALUES (?, ?, ?)",
                (uniqe, analyze, result)
            )
            connection.commit()
            QMessageBox.information(self, "Успех", "Результаты успешно сохранены")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить результаты: {e}")
        finally:
            connection.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Электронный справочник для врача")
        self.stacked_widget = QStackedWidget()

        self.login_page = LoginPage(self.stacked_widget)
        self.main_menu_page = MainMenuPage(self.stacked_widget)
        self.patients_page = PatientsPage(self.stacked_widget)
        self.analyze_page = AnalyzePage(self.stacked_widget)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_menu_page)
        self.stacked_widget.addWidget(self.patients_page)
        self.stacked_widget.addWidget(self.analyze_page)

        self.setCentralWidget(self.stacked_widget)

        self.set_close_confirmation()

    def set_close_confirmation(self):
        self.closeEvent = self.confirm_close

    def confirm_close(self, event):
        reply = QMessageBox()
        reply.setWindowTitle("Выход")
        reply.setText("Вы точно хотите закрыть приложение?")
        yes_button = reply.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = reply.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        reply.exec()

        if reply.clickedButton() == yes_button:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
