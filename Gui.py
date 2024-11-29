import sys
import json
from PyQt5.Qt import QIcon
from PyQt5.QtWidgets import QStyle,QSystemTrayIcon,QMenu,QAction,QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from Duifenyi_client import DuifenyiClient  # 导入DuifenyiClient类
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")#设置唯一标识符
icon_path = './resource/img/icon.svg'

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = self.__read_last_user()
        self.__initUI()
        self.__load_last_user()
    def __initUI(self):
        self.setWindowTitle("登录")
        self.setWindowIcon(QIcon(icon_path))
        self.resize(800, 400)
        self.move(self.__screen().width() // 2 - self.width() // 2, self.__screen().height() // 2 - self.height() // 2)
        self.setFixedSize(800, 400)
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
        login_button.clicked.connect(self.__handle_login)
        layout.addWidget(login_button, 2, 1)

    def __read_last_user(self):
        data = {}
        # 通过捕获异常，显式的忽视错误
        try:
            with open('./resource/data/user', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            return data
    def __save_user(self):
        with open('./resource/data/user', 'w', encoding='utf-8') as f:
            json.dump(self.current_user, f, ensure_ascii=False, indent=4)
    def __load_last_user(self):
        if self.current_user!= {}:
            self.username.setText(self.current_user['user'])
            self.password.setText(self.current_user['pwd'])
        else:
            self.username.setText('')
            self.password.setText('')
    def __handle_login(self):
        username = self.username.text()
        password = self.password.text()
        if self.current_user=={} or username != self.current_user['user'] or password != self.current_user['pwd']:
            self.current_user["user"] = username
            self.current_user["pwd"] = password
            self.__save_user()
        homework_data = {}
        try:
            with open('./resource/data/homework', 'r', encoding='utf-8') as f:
                homework_data = json.load(f)
            self.__accept(homework_data)
            # 显式的抛错
        except json.JSONDecodeError:
            self.__accept(homework_data)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def __accept(self, homework_data):
        self.close()
        self.main = MainWindow(homework_data, self.current_user)
        self.main.show()

    def __screen(self):
        return QApplication.desktop().screenGeometry()

class MainWindow(QMainWindow):
    def __init__(self, homework_data, current_user):
        super().__init__()
        self.homework_data = homework_data
        self.username = current_user["user"]
        self.password = current_user["pwd"]
        self.__initUI()
        self.__initTray()

    def __initUI(self):
        self.setWindowTitle("对分易作业备忘录")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        # self.setWindowTitle("对分易作业备忘录")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)  # 固定窗口大小
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        # 添加更新按钮
        self.update_button = QPushButton("更新", self)
        self.update_button.clicked.connect(self.__update_homework)  # 连接点击事件
        layout.addWidget(self.update_button)
        self.memo_label = QLabel(" ")
        self.memo_label.setWordWrap(True)  # 允许换行
        layout.addWidget(self.memo_label)
        #绘制窗口
        self.__display_homework(self.homework_data)

    def __initTray(self):#初始托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip('对分易作业备忘录')# 设置鼠标悬停时显示的文本
        self.tray_icon.activated.connect(self.__iconActivated)#连接响应
        self.tray_icon.setVisible(True)
        self.menu = QMenu()
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.__show_window)
        hide_action = QAction("隐藏窗口", self)
        hide_action.triggered.connect(self.__hide_window)
        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self.__quit_application)
        self.menu.addAction(show_action)
        self.menu.addAction(hide_action)
        self.menu.addAction(quit_action)
    def __iconActivated(self,reason):#响应事件
        if reason == QSystemTrayIcon.Trigger:  # 对于单击响应
            if self.isMinimized():
                self.showNormal()
            else :
                self.show()
        elif reason == QSystemTrayIcon.Context:
            self.tray_icon.setContextMenu(self.menu)
    def __show_window(self):
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()

    def __hide_window(self):
        self.hide()
    def __quit_application(self):
        self.tray_icon.hide()
        QApplication.quit()
    def closeEvent(self, event):
        event.ignore()
        self.__hide_window()
    def __update_homework(self):
        client = DuifenyiClient(username=self.username, password=self.password)
        try:
            self.homework_data = client.get()
            self.__display_homework(self.homework_data)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            print("更新按钮被点击，执行更新操作")

    def __display_homework(self, homework_data):
        if homework_data != {}:
            sorted_homework_items = []
            for course, homeworks in homework_data.items():
                for homework in homeworks:
                    due_date = homework['截止时间:']
                    homework_item = (due_date, course, homework['作业:'])
                    sorted_homework_items.append(homework_item)
            sorted_homework_items.sort(key=lambda item: item[0])
            memo_text = ""
            for due_date, course, homework_name in sorted_homework_items:
                memo_text += f"{course} ({due_date}) {homework_name}\n"
            self.memo_label.setText(memo_text)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     login_window = LoginWindow()
#     login_window.show()
#     sys.exit(app.exec_())