# gui.py
import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from Duifenyi_client import DuifenyiClient  # 导入DuofenyiClient类

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("登录")
        self.resize(800, 400)
        self.move(self.screen().width() // 2 - self.width() // 2, self.screen().height() // 2 - self.height() // 2)
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
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button, 2, 1)
    def __read_user(self):
        data = {}
        with open('./resource/data/user', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    def __save_user(self,username,password):
        user = {}
        user['user']=username
        user['pwd']=password
        with open('./resource/data/user','w',encoding='utf-8') as f:
            json.dump(user,f,ensure_ascii=False,indent=4)
    def handle_login(self):
        username = self.username.text()
        password = self.password.text()
        self.current_user[username]=password
        # 只要读了，就要卡死......
        data = self.__read_user()
        if data == {}:
            print('empty')
        # print(data)
        else:
            if username not in data:
                self.__save_user(username=username,password=password)

        try:
            homework_data = {}
            with open('./resource/data/homework','r',encoding='utf-8') as f:
                homework_data = json.load(f)
            self.accept(homework_data)
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def accept(self, homework_data):
        self.close()
        self.main = MainWindow(homework_data)
        self.main.show()

    def screen(self):
        return QApplication.desktop().screenGeometry()


class MainWindow(QMainWindow):
    def __init__(self, homework_data):
        super().__init__()
        self.homework_data = homework_data
        # self.username=current_user.items()[0][0]
        # self.password=current_user.items()[0][1]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("对分易作业备忘录")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)  # 固定窗口大小

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # 添加更新按钮
        self.update_button = QPushButton("更新", self)
        self.update_button.clicked.connect(self.update_homework)  # 连接点击事件
        layout.addWidget(self.update_button)

        self.memo_label = QLabel("这里将显示备忘录内容")
        self.memo_label.setWordWrap(True)  # 允许换行
        layout.addWidget(self.memo_label)

        self.display_homework(self.homework_data)

    def update_homework(self):
        # client = DuifenyiClient(username=self.username,password=self.password)
        # self.homework_data= client.get()
        # self.initUI()
        print("更新按钮被点击，执行更新操作")

    def display_homework(self, homework_data):
        # 将作业数据按照截止日期排序
        sorted_homework_items = []
        for course, homeworks in homework_data.items():
            for homework in homeworks:
                due_date = homework['截止时间:']  # 提取截止日期
                homework_item = (due_date, course, homework['作业:'])  # 创建元组 (截止日期, 课程名称, 作业名称)
                sorted_homework_items.append(homework_item)

        # 按截止日期升序排序
        sorted_homework_items.sort(key=lambda item: item[0])

        # 构建展示文本
        memo_text = ""
        for due_date, course, homework_name in sorted_homework_items:
            memo_text += f"{course} ({due_date}) {homework_name}\n"

        self.memo_label.setText(memo_text)  # 将格式化的文本设置为标签的内容

app = QApplication(sys.argv)
login_window = LoginWindow()
login_window.show()
sys.exit(app.exec_())