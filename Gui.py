import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("登录")
        self.resize(800, 400)  # 设置窗口大小为原来的两倍
        self.move(self.screen().width() // 2 - self.width() // 2, self.screen().height() // 2 - self.height() // 2)  # 初始绘制在屏幕中间
        self.setFixedSize(800, 400)  # 设置固定大小
        layout = QGridLayout(self)
        self.username = QLineEdit(self)
        self.username.setPlaceholderText("请输入用户名")
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("请输入密码")

        layout.addWidget(QLabel("用户名:"), 0, 0)
        layout.addWidget(self.username, 0, 1)
        layout.addWidget(QLabel("密码:"), 1, 0)
        layout.addWidget(self.password, 1, 1)

        login_button = QPushButton("登录", self)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button, 2, 1)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        # 这里应该有验证逻辑，这里假设用户名和密码都是"admin"
        if username == "admin" and password == "password":
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")

    def accept(self):
        self.close()
        self.main = MainWindow()
        self.main.show()

    def screen(self):
        return QApplication.desktop().screenGeometry()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("对分易作业备忘录")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.memo_label = QLabel("这里将显示备忘录内容")
        layout.addWidget(self.memo_label)

        self.load_memo()

    def load_memo(self):
        try:
            with open("courses.json", "r") as file:
                data = json.load(file)
                memo_text = ""
                for course in data["courses"]:
                    memo_text += f"课程名称：{course['name']}\n截止日期：{course['due_date']}\n\n"
                self.memo_label.setText(memo_text)
        except FileNotFoundError:
            self.memo_label.setText("备忘录文件不存在。")
        except json.JSONDecodeError:
            self.memo_label.setText("备忘录文件格式错误。")

app = QApplication(sys.argv)
login_window = LoginWindow()
login_window.show()
sys.exit(app.exec_())