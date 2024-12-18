import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QStackedWidget, QMessageBox, QTableWidget, QTableWidgetItem,
    QFormLayout
)
from PyQt6.QtCore import Qt
import sqlite3

class PatientLoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.uniqe_input_value = None

        layout = QVBoxLayout()
        self.label = QLabel("Введите уникальный номер пациента:")
        self.uniqe_input = QLineEdit()
        self.login_button = QPushButton("Войти")

        layout.addWidget(self.label)
        layout.addWidget(self.uniqe_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.login_button.clicked.connect(self.check_uniqe)

    def check_uniqe(self):
        uniqe = self.uniqe_input.text().strip()
        if not uniqe:
            QMessageBox.warning(self, "Ошибка", "Уникальный номер не может быть пустым.")
            return

        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patients WHERE uniqe = ? COLLATE NOCASE", (uniqe,))
        patient = cursor.fetchone()
        connection.close()

        if patient:
            self.uniqe_input_value = uniqe
            self.stacked_widget.widget(1).load_patient_info(uniqe)
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Ошибка", "Уникальный номер не найден.")

class PatientInfoPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        self.label = QLabel("Личная информация пациента")
        self.info_label = QLabel()
        self.results_button = QPushButton("Посмотреть результаты анализов")
        self.back_button = QPushButton("Назад")

        layout.addWidget(self.label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.results_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.results_button.clicked.connect(self.go_to_results_page)
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    def load_patient_info(self, uniqe):
        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name, age, gender, uniqe FROM patients WHERE uniqe = ? COLLATE NOCASE", (uniqe,))
        patient = cursor.fetchone()
        connection.close()

        if patient:
            self.info_label.setText(
                f"Имя: {patient[0]}\n"
                f"Возраст: {patient[1]}\n"
                f"Пол: {patient[2]}\n"
                f"Уникальный номер: {patient[3]}"
            )
        else:
            self.info_label.setText("Информация о пациенте не найдена.")

    def go_to_results_page(self):
        patient_login_page = self.stacked_widget.widget(0)
        uniqe = patient_login_page.uniqe_input_value
        self.stacked_widget.widget(2).load_results(uniqe)
        self.stacked_widget.setCurrentIndex(2)

class PatientResultsPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        self.label = QLabel("Результаты анализов")
        self.results_label = QLabel()
        self.back_button = QPushButton("Назад")

        layout.addWidget(self.label)
        layout.addWidget(self.results_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    def load_results(self, uniqe):
        connection = sqlite3.connect('patients.db')
        cursor = connection.cursor()
        cursor.execute("SELECT analyze, result FROM results WHERE uniqe = ? COLLATE NOCASE", (uniqe,))
        results = cursor.fetchall()
        connection.close()

        if results:
            results_text = "\n".join([f"Обследование: {row[0]} - Результат: {row[1]}" for row in results])
            self.results_label.setText(results_text)
        else:
            self.results_label.setText("Результаты анализов отсутствуют.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Электронный справочник для пациента")
        self.stacked_widget = QStackedWidget()

        self.patient_login_page = PatientLoginPage(self.stacked_widget)
        self.patient_info_page = PatientInfoPage(self.stacked_widget)
        self.patient_results_page = PatientResultsPage(self.stacked_widget)

        self.stacked_widget.addWidget(self.patient_login_page)
        self.stacked_widget.addWidget(self.patient_info_page)
        self.stacked_widget.addWidget(self.patient_results_page)

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
