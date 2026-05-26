"""
Застосунок для запису на прийом до лікаря
Standalone PyQt5 desktop application з вбудованою SQLite базою даних.

Тестові акаунти лікарів:
  Логін: kovalenko  | Пароль: admin
  Логін: sydorenko  | Пароль: admin
"""

import sys
import sqlite3
import os
from datetime import date

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap

# ─────────────────────────────────────────────────────────────────────────────
#  ВИПРАВЛЕННЯ: Правильний шлях до БД для .exe та .py
# ─────────────────────────────────────────────────────────────────────────────
def get_base_dir():
    """
    Повертає базову директорію:
    - При запуску як .exe (PyInstaller) — папка поруч з exe
    - При запуску як .py — папка зі скриптом
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(get_base_dir(), "doctor_app.db")
# ─────────────────────────────────────────────────────────────────────────────


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            login    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor_name  TEXT NOT NULL,
            date         TEXT NOT NULL
        )
    """)
    # Дефолтні лікарі
    c.execute("INSERT OR IGNORE INTO users (name, login, password, role) "
              "VALUES ('Лікар Коваленко', 'kovalenko', 'admin', 'doctor')")
    c.execute("INSERT OR IGNORE INTO users (name, login, password, role) "
              "VALUES ('Лікар Сидоренко', 'sydorenko', 'admin', 'doctor')")
    conn.commit()
    conn.close()


#  Стилі (загальна палітра)
COLOR_BG        = "#F0F4FA"
COLOR_CARD      = "#FFFFFF"
COLOR_PRIMARY   = "#2563EB"   # синій
COLOR_PRIMARY_H = "#1D4ED8"
COLOR_SUCCESS   = "#16A34A"
COLOR_SUCCESS_H = "#15803D"
COLOR_DANGER    = "#DC2626"
COLOR_DANGER_H  = "#B91C1C"
COLOR_MUTED     = "#64748B"
COLOR_BORDER    = "#CBD5E1"
COLOR_TEXT      = "#1E293B"
COLOR_HEADER_BG = "#1E40AF"

BASE_STYLE = f"""
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 14px;
        color: {COLOR_TEXT};
    }}
    QMainWindow, QStackedWidget, #root_widget {{
        background-color: {COLOR_BG};
    }}
    QLineEdit, QComboBox, QDateEdit {{
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        background: #FFFFFF;
        font-size: 14px;
        min-height: 36px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 2px solid {COLOR_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        background: #FFFFFF;
        selection-background-color: {COLOR_PRIMARY};
        selection-color: #FFFFFF;
    }}
    QTableWidget {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        gridline-color: #E2E8F0;
        background: #FFFFFF;
        alternate-background-color: #F8FAFC;
    }}
    QTableWidget::item {{
        padding: 8px 12px;
    }}
    QTableWidget::item:selected {{
        background-color: #DBEAFE;
        color: {COLOR_TEXT};
    }}
    QHeaderView::section {{
        background-color: {COLOR_HEADER_BG};
        color: #FFFFFF;
        font-weight: bold;
        padding: 10px 12px;
        border: none;
        font-size: 13px;
    }}
    QScrollBar:vertical {{
        width: 8px;
        background: #F1F5F9;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: #94A3B8;
        border-radius: 4px;
    }}
"""

def btn_style(bg, hover, text_color="#FFFFFF", outlined=False):
    if outlined:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {bg};
                border: 2px solid {bg};
                border-radius: 8px;
                padding: 9px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {bg};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{ background-color: {hover}; }}
        """
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text_color};
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover   {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {hover}; }}
        QPushButton:disabled {{ background-color: #94A3B8; color: #E2E8F0; }}
    """


#  Допоміжні компоненти
def make_card(min_width=440, max_width=480):
    """Повертає QFrame-картку з тінню."""
    card = QFrame()
    card.setMinimumWidth(min_width)
    card.setMaximumWidth(max_width)
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {COLOR_CARD};
            border-radius: 16px;
            border: 1px solid {COLOR_BORDER};
        }}
    """)
    return card


def make_label(text, font_size=14, bold=False, color=COLOR_TEXT, align=None):
    lbl = QLabel(text)
    font = QFont()
    font.setPointSize(font_size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    if align:
        lbl.setAlignment(align)
    return lbl


def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {COLOR_BORDER}; background: {COLOR_BORDER}; border: none; max-height: 1px;")
    return line


def show_message(parent, title, text, kind="info"):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    if kind == "error":
        msg.setIcon(QMessageBox.Critical)
    elif kind == "success":
        msg.setIcon(QMessageBox.Information)
    else:
        msg.setIcon(QMessageBox.Information)
    msg.setStyleSheet(f"QLabel {{ font-size: 14px; }} QMessageBox {{ background: {COLOR_CARD}; }}")
    msg.exec_()


# Логін
class LoginScreen(QWidget):
    def __init__(self, on_login_success, on_go_register):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_go_register   = on_go_register
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Заголовок-банер
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                              f"stop:0 {COLOR_HEADER_BG}, stop:1 {COLOR_PRIMARY});")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(32, 0, 32, 0)
        icon_lbl = QLabel("🏥")
        icon_lbl.setStyleSheet("font-size: 36px; background: transparent; border: none;")
        title_lbl = make_label("Запис до Лікаря", 22, bold=True, color="#FFFFFF")
        sub_lbl   = make_label("Медична інформаційна система", 11, color="#BFDBFE")
        col = QVBoxLayout()
        col.addWidget(title_lbl)
        col.addWidget(sub_lbl)
        h_lay.addWidget(icon_lbl)
        h_lay.addSpacing(12)
        h_lay.addLayout(col)
        h_lay.addStretch()
        root.addWidget(header)

        # Центральна зона
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        root.addLayout(center, 1)

        card = make_card()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 36, 40, 36)
        card_lay.setSpacing(16)

        card_lay.addWidget(make_label("Вхід у систему", 18, bold=True,
                                      align=Qt.AlignCenter))
        card_lay.addWidget(make_label("Введіть ваші облікові дані", 12,
                                      color=COLOR_MUTED, align=Qt.AlignCenter))
        card_lay.addSpacing(8)
        card_lay.addWidget(make_separator())
        card_lay.addSpacing(8)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)

        self.inp_login = QLineEdit()
        self.inp_login.setPlaceholderText("Ваш логін")
        self.inp_pass  = QLineEdit()
        self.inp_pass.setPlaceholderText("Ваш пароль")
        self.inp_pass.setEchoMode(QLineEdit.Password)

        lbl_l = make_label("Логін:", 13, bold=True)
        lbl_p = make_label("Пароль:", 13, bold=True)
        form.addRow(lbl_l, self.inp_login)
        form.addRow(lbl_p, self.inp_pass)
        card_lay.addLayout(form)

        self.lbl_error = make_label("", 12, color=COLOR_DANGER, align=Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        card_lay.addWidget(self.lbl_error)

        btn_login = QPushButton("🔐  Увійти")
        btn_login.setStyleSheet(btn_style(COLOR_PRIMARY, COLOR_PRIMARY_H))
        btn_login.setMinimumHeight(44)
        btn_login.clicked.connect(self._do_login)
        self.inp_pass.returnPressed.connect(self._do_login)
        card_lay.addWidget(btn_login)

        card_lay.addWidget(make_separator())

        reg_row = QHBoxLayout()
        reg_row.addStretch()
        reg_row.addWidget(make_label("Немає акаунту?", 12, color=COLOR_MUTED))
        reg_row.addSpacing(6)
        btn_reg = QPushButton("Зареєструватися")
        btn_reg.setFlat(True)
        btn_reg.setCursor(Qt.PointingHandCursor)
        btn_reg.setStyleSheet(f"""
            QPushButton {{
                color: {COLOR_PRIMARY}; background: transparent; border: none;
                font-size: 13px; font-weight: bold; padding: 0;
            }}
            QPushButton:hover {{ text-decoration: underline; color: {COLOR_PRIMARY_H}; }}
        """)
        btn_reg.clicked.connect(self.on_go_register)
        reg_row.addWidget(btn_reg)
        reg_row.addStretch()
        card_lay.addLayout(reg_row)

        center.addWidget(card, alignment=Qt.AlignCenter)

        # Підказка
        hint = make_label(
            "Лікарі: kovalenko / admin    або    sydorenko / admin",
            10, color=COLOR_MUTED, align=Qt.AlignCenter
        )
        root.addWidget(hint)
        root.addSpacing(16)

    def _do_login(self):
        login    = self.inp_login.text().strip()
        password = self.inp_pass.text().strip()
        if not login or not password:
            self.lbl_error.setText("Заповніть усі поля!")
            return
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE login=? AND password=?", (login, password)
        ).fetchone()
        conn.close()
        if not user:
            self.lbl_error.setText("❌  Невірний логін або пароль")
            self.inp_pass.clear()
        else:
            self.lbl_error.setText("")
            self.inp_login.clear()
            self.inp_pass.clear()
            self.on_login_success(dict(user))

    def reset(self):
        self.inp_login.clear()
        self.inp_pass.clear()
        self.lbl_error.setText("")


#  ЕКРАН: Реєстрація
class RegisterScreen(QWidget):
    def __init__(self, on_registered, on_go_login):
        super().__init__()
        self.on_registered = on_registered
        self.on_go_login   = on_go_login
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                              f"stop:0 #065F46, stop:1 {COLOR_SUCCESS});")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(32, 0, 32, 0)
        icon_lbl = QLabel("🏥")
        icon_lbl.setStyleSheet("font-size: 36px; background: transparent; border: none;")
        t1 = make_label("Запис до Лікаря", 22, bold=True, color="#FFFFFF")
        t2 = make_label("Медична інформаційна система", 11, color="#A7F3D0")
        col = QVBoxLayout(); col.addWidget(t1); col.addWidget(t2)
        h_lay.addWidget(icon_lbl); h_lay.addSpacing(12); h_lay.addLayout(col); h_lay.addStretch()
        root.addWidget(header)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)
        root.addLayout(center, 1)

        card = make_card()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 36, 40, 36)
        card_lay.setSpacing(14)

        card_lay.addWidget(make_label("Реєстрація пацієнта", 18, bold=True, align=Qt.AlignCenter))
        card_lay.addWidget(make_label("Створіть свій особистий акаунт", 12,
                                      color=COLOR_MUTED, align=Qt.AlignCenter))
        card_lay.addSpacing(4)
        card_lay.addWidget(make_separator())
        card_lay.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)

        self.inp_name  = QLineEdit(); self.inp_name.setPlaceholderText("Наприклад: Іванов Іван Іванович")
        self.inp_login = QLineEdit(); self.inp_login.setPlaceholderText("Унікальний логін")
        self.inp_pass  = QLineEdit(); self.inp_pass.setPlaceholderText("Пароль")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass2 = QLineEdit(); self.inp_pass2.setPlaceholderText("Повторіть пароль")
        self.inp_pass2.setEchoMode(QLineEdit.Password)

        for lbl_txt, widget in [
            ("ПІБ:", self.inp_name),
            ("Логін:", self.inp_login),
            ("Пароль:", self.inp_pass),
            ("Підтвердження:", self.inp_pass2),
        ]:
            form.addRow(make_label(lbl_txt, 13, bold=True), widget)
        card_lay.addLayout(form)

        self.lbl_msg = make_label("", 12, color=COLOR_DANGER, align=Qt.AlignCenter)
        self.lbl_msg.setWordWrap(True)
        card_lay.addWidget(self.lbl_msg)

        btn_reg = QPushButton("✅  Створити акаунт")
        btn_reg.setStyleSheet(btn_style(COLOR_SUCCESS, COLOR_SUCCESS_H))
        btn_reg.setMinimumHeight(44)
        btn_reg.clicked.connect(self._do_register)
        card_lay.addWidget(btn_reg)

        card_lay.addWidget(make_separator())

        back_row = QHBoxLayout()
        back_row.addStretch()
        back_row.addWidget(make_label("Вже є акаунт?", 12, color=COLOR_MUTED))
        back_row.addSpacing(6)
        btn_login = QPushButton("Увійти")
        btn_login.setFlat(True)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                color: {COLOR_PRIMARY}; background: transparent; border: none;
                font-size: 13px; font-weight: bold; padding: 0;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        btn_login.clicked.connect(self.on_go_login)
        back_row.addWidget(btn_login)
        back_row.addStretch()
        card_lay.addLayout(back_row)

        center.addWidget(card, alignment=Qt.AlignCenter)
        root.addSpacing(16)

    def _do_register(self):
        name  = self.inp_name.text().strip()
        login = self.inp_login.text().strip()
        pwd   = self.inp_pass.text().strip()
        pwd2  = self.inp_pass2.text().strip()

        if not all([name, login, pwd, pwd2]):
            self.lbl_msg.setStyleSheet(f"color: {COLOR_DANGER}; background: transparent; border: none;")
            self.lbl_msg.setText("❌  Заповніть усі поля!")
            return
        if pwd != pwd2:
            self.lbl_msg.setStyleSheet(f"color: {COLOR_DANGER}; background: transparent; border: none;")
            self.lbl_msg.setText("❌  Паролі не співпадають!")
            return
        if len(pwd) < 3:
            self.lbl_msg.setStyleSheet(f"color: {COLOR_DANGER}; background: transparent; border: none;")
            self.lbl_msg.setText("❌  Пароль занадто короткий (мін. 3 символи)!")
            return

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (name, login, password, role) VALUES (?, ?, ?, 'patient')",
                (name, login, pwd)
            )
            conn.commit()
            conn.close()
            self.lbl_msg.setStyleSheet(f"color: {COLOR_SUCCESS}; background: transparent; border: none;")
            self.lbl_msg.setText("✅  Реєстрація успішна! Переходьте до входу.")
            self._clear_fields()
            self.on_registered()
        except sqlite3.IntegrityError:
            self.lbl_msg.setStyleSheet(f"color: {COLOR_DANGER}; background: transparent; border: none;")
            self.lbl_msg.setText("❌  Цей логін вже зайнятий!")

    def _clear_fields(self):
        for w in [self.inp_name, self.inp_login, self.inp_pass, self.inp_pass2]:
            w.clear()

    def reset(self):
        self._clear_fields()
        self.lbl_msg.setText("")


# Кабінет пацієнта
class PatientCabinetScreen(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout    = on_logout
        self.patient_name = ""
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar
        navbar = QFrame()
        navbar.setFixedHeight(64)
        navbar.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                             f"stop:0 {COLOR_HEADER_BG}, stop:1 {COLOR_PRIMARY});")
        nb_lay = QHBoxLayout(navbar)
        nb_lay.setContentsMargins(24, 0, 24, 0)

        icon_title = QHBoxLayout()
        nav_icon = QLabel("🏥")
        nav_icon.setStyleSheet("font-size: 26px; background: transparent; border: none;")
        nav_title = make_label("Кабінет Пацієнта", 16, bold=True, color="#FFFFFF")
        icon_title.addWidget(nav_icon); icon_title.addSpacing(8); icon_title.addWidget(nav_title)
        nb_lay.addLayout(icon_title)
        nb_lay.addStretch()

        self.lbl_user = make_label("", 12, color="#BFDBFE")
        nb_lay.addWidget(self.lbl_user)
        nb_lay.addSpacing(16)

        btn_out = QPushButton("🚪  Вийти")
        btn_out.setStyleSheet(btn_style(COLOR_DANGER, COLOR_DANGER_H))
        btn_out.setFixedHeight(36)
        btn_out.clicked.connect(self._do_logout)
        nb_lay.addWidget(btn_out)
        root.addWidget(navbar)

        # Основний вміст
        scroll_area = QVBoxLayout()
        scroll_area.setContentsMargins(40, 32, 40, 32)
        scroll_area.setSpacing(24)

        # Вітання
        self.lbl_welcome = make_label("", 20, bold=True)
        scroll_area.addWidget(self.lbl_welcome)
        scroll_area.addWidget(make_label("Оберіть лікаря та зручний час для візиту", 13, color=COLOR_MUTED))
        scroll_area.addWidget(make_separator())

        # Картка форми
        card = make_card(min_width=500, max_width=600)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(36, 32, 36, 32)
        card_lay.setSpacing(16)

        card_lay.addWidget(make_label("📋  Новий запис на прийом", 16, bold=True))
        card_lay.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.combo_doctor = QComboBox()
        self.combo_doctor.setMinimumHeight(40)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setMinimumDate(QDate.currentDate())
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setMinimumHeight(40)
        self.date_picker.setDisplayFormat("dd.MM.yyyy")

        form.addRow(make_label("Лікар:", 13, bold=True), self.combo_doctor)
        form.addRow(make_label("Дата:", 13, bold=True),   self.date_picker)
        card_lay.addLayout(form)

        self.lbl_result = make_label("", 13, align=Qt.AlignCenter)
        self.lbl_result.setWordWrap(True)
        card_lay.addWidget(self.lbl_result)

        btn_submit = QPushButton("✅  Підтвердити запис")
        btn_submit.setStyleSheet(btn_style(COLOR_SUCCESS, COLOR_SUCCESS_H))
        btn_submit.setMinimumHeight(46)
        btn_submit.clicked.connect(self._do_book)
        card_lay.addWidget(btn_submit)

        scroll_area.addWidget(card)
        scroll_area.addStretch()
        root.addLayout(scroll_area, 1)

    def load(self, user: dict):
        self.patient_name = user["name"]
        self.lbl_user.setText(f"👤  {self.patient_name}")
        self.lbl_welcome.setText(f"Вітаємо, {self.patient_name}! 👋")
        self.lbl_result.setText("")
        self._load_doctors()
        self.date_picker.setDate(QDate.currentDate())

    def _load_doctors(self):
        self.combo_doctor.clear()
        self.combo_doctor.addItem("-- Оберіть лікаря --", "")
        conn = get_connection()
        rows = conn.execute("SELECT name FROM users WHERE role='doctor'").fetchall()
        conn.close()
        for row in rows:
            self.combo_doctor.addItem(row["name"], row["name"])

    def _do_book(self):
        doctor = self.combo_doctor.currentData()
        dt     = self.date_picker.date().toString("yyyy-MM-dd")
        if not doctor:
            self.lbl_result.setStyleSheet(f"color: {COLOR_DANGER}; background: transparent; border: none;")
            self.lbl_result.setText("❌  Будь ласка, оберіть лікаря!")
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date) VALUES (?, ?, ?)",
            (self.patient_name, doctor, dt)
        )
        conn.commit()
        conn.close()

        display_date = self.date_picker.date().toString("dd.MM.yyyy")
        self.lbl_result.setStyleSheet(f"color: {COLOR_SUCCESS}; background: transparent; border: none;")
        self.lbl_result.setText(f"✅  Ви записані до {doctor} на {display_date}!")
        self.combo_doctor.setCurrentIndex(0)
        self.date_picker.setDate(QDate.currentDate())

    def _do_logout(self):
        self.patient_name = ""
        self.on_logout()


# Панель лікаря
class DoctorPanelScreen(QWidget):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout   = on_logout
        self.doctor_name = ""
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar
        navbar = QFrame()
        navbar.setFixedHeight(64)
        navbar.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                             f"stop:0 #065F46, stop:1 {COLOR_SUCCESS});")
        nb_lay = QHBoxLayout(navbar)
        nb_lay.setContentsMargins(24, 0, 24, 0)

        icon_title = QHBoxLayout()
        nav_icon = QLabel("👨‍⚕️")
        nav_icon.setStyleSheet("font-size: 26px; background: transparent; border: none;")
        nav_title = make_label("Панель Лікаря", 16, bold=True, color="#FFFFFF")
        icon_title.addWidget(nav_icon); icon_title.addSpacing(8); icon_title.addWidget(nav_title)
        nb_lay.addLayout(icon_title)
        nb_lay.addStretch()

        self.lbl_user = make_label("", 12, color="#A7F3D0")
        nb_lay.addWidget(self.lbl_user)
        nb_lay.addSpacing(16)

        btn_refresh = QPushButton("🔄  Оновити")
        btn_refresh.setStyleSheet(btn_style("transparent", "#A7F3D0", "#FFFFFF", outlined=True))
        btn_refresh.setFixedHeight(36)
        btn_refresh.clicked.connect(self._load_appointments)
        nb_lay.addWidget(btn_refresh)
        nb_lay.addSpacing(8)

        btn_out = QPushButton("🚪  Вийти")
        btn_out.setStyleSheet(btn_style(COLOR_DANGER, COLOR_DANGER_H))
        btn_out.setFixedHeight(36)
        btn_out.clicked.connect(self._do_logout)
        nb_lay.addWidget(btn_out)
        root.addWidget(navbar)

        # Контент
        content = QVBoxLayout()
        content.setContentsMargins(40, 28, 40, 32)
        content.setSpacing(16)

        self.lbl_title = make_label("", 20, bold=True)
        content.addWidget(self.lbl_title)
        content.addWidget(make_label("Список пацієнтів, записаних на прийом", 13, color=COLOR_MUTED))
        content.addWidget(make_separator())

        # Статистика
        self.stat_frame = QFrame()
        self.stat_frame.setStyleSheet(f"""
            QFrame {{
                background: #EFF6FF;
                border-radius: 10px;
                border: 1px solid #BFDBFE;
            }}
        """)
        stat_lay = QHBoxLayout(self.stat_frame)
        stat_lay.setContentsMargins(24, 14, 24, 14)
        self.lbl_total = make_label("Всього записів: —", 14, bold=True, color=COLOR_PRIMARY)
        stat_lay.addWidget(self.lbl_total)
        stat_lay.addStretch()
        self.lbl_today = make_label("На сьогодні: —", 14, color=COLOR_MUTED)
        stat_lay.addWidget(self.lbl_today)
        content.addWidget(self.stat_frame)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["  №", "  Ім'я пацієнта", "  Дата візиту"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(300)
        content.addWidget(self.table, 1)

        root.addLayout(content, 1)

    def load(self, user: dict):
        self.doctor_name = user["name"]
        self.lbl_user.setText(f"👤  {self.doctor_name}")
        self.lbl_title.setText(f"Записи пацієнтів — {self.doctor_name}")
        self._load_appointments()

    def _load_appointments(self):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM appointments WHERE doctor_name=? ORDER BY date ASC",
            (self.doctor_name,)
        ).fetchall()
        conn.close()

        today_str = date.today().strftime("%Y-%m-%d")
        today_count = sum(1 for r in rows if r["date"] == today_str)

        self.lbl_total.setText(f"Всього записів: {len(rows)}")
        self.lbl_today.setText(f"На сьогодні: {today_count}")

        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)

            num_item = QTableWidgetItem(f"  {i + 1}")
            num_item.setTextAlignment(Qt.AlignCenter)

            name_item = QTableWidgetItem(f"  {row['patient_name']}")
            name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            # Форматуємо дату
            try:
                d = date.fromisoformat(row['date'])
                display = d.strftime("%d.%m.%Y")
            except Exception:
                display = row['date']

            date_item = QTableWidgetItem(f"  {display}")
            date_item.setTextAlignment(Qt.AlignCenter)

            # Підсвітка сьогодні
            if row["date"] == today_str:
                highlight = QColor("#DCFCE7")
                for item in [num_item, name_item, date_item]:
                    item.setBackground(highlight)

            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, name_item)
            self.table.setItem(i, 2, date_item)
            self.table.setRowHeight(i, 44)

        if len(rows) == 0:
            self.table.insertRow(0)
            empty = QTableWidgetItem("Записів ще немає")
            empty.setTextAlignment(Qt.AlignCenter)
            empty.setForeground(QColor(COLOR_MUTED))
            self.table.setSpan(0, 0, 1, 3)
            self.table.setItem(0, 0, empty)

    def _do_logout(self):
        self.doctor_name = ""
        self.on_logout()


#  Головне вікно
class MainWindow(QMainWindow):
    PAGE_LOGIN    = 0
    PAGE_REGISTER = 1
    PAGE_PATIENT  = 2
    PAGE_DOCTOR   = 3

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Застосунок для запису на прийом до лікаря.")
        self.resize(860, 640)
        self.setMinimumSize(720, 560)
        self.setStyleSheet(BASE_STYLE)

        central = QWidget()
        central.setObjectName("root_widget")
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        main_lay.addWidget(self.stack)

        # Екрани
        self.screen_login    = LoginScreen(self._on_login, self._go_register)
        self.screen_register = RegisterScreen(self._on_registered, self._go_login)
        self.screen_patient  = PatientCabinetScreen(self._on_logout)
        self.screen_doctor   = DoctorPanelScreen(self._on_logout)

        self.stack.addWidget(self.screen_login)     # 0
        self.stack.addWidget(self.screen_register)  # 1
        self.stack.addWidget(self.screen_patient)   # 2
        self.stack.addWidget(self.screen_doctor)    # 3

        self.stack.setCurrentIndex(self.PAGE_LOGIN)

    # Навігація
    def _on_login(self, user: dict):
        if user["role"] == "doctor":
            self.screen_doctor.load(user)
            self.stack.setCurrentIndex(self.PAGE_DOCTOR)
        else:
            self.screen_patient.load(user)
            self.stack.setCurrentIndex(self.PAGE_PATIENT)

    def _go_register(self):
        self.screen_register.reset()
        self.stack.setCurrentIndex(self.PAGE_REGISTER)

    def _go_login(self):
        self.screen_login.reset()
        self.stack.setCurrentIndex(self.PAGE_LOGIN)

    def _on_registered(self):
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, self._go_login)

    def _on_logout(self):
        self.screen_login.reset()
        self.stack.setCurrentIndex(self.PAGE_LOGIN)


#  Точка входу
def main():
    init_database()
    app = QApplication(sys.argv)
    app.setApplicationName("Запис до Лікаря")

    # HiDPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
