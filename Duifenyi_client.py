import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
course_count = 9

class DuifenyiClient:
    def __init__(self,username,password):
        self.username=username
        self.password = password
        self.session = requests.session()
    def __login(self):
        login_url = 'https://www.duifene.com/AppCode/LoginInfo.ashx'
        guid = self.__getguid()
        headers = {
            "user - agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "x-requested -with": "XMLHttpRequest",
            "referer": "https://www.duifene.com/Home.aspx",
            "origin": "https://www.duifene.com"
        }
        data = {
            "action": "login",
            "loginname": self.username,
            "password": self.password,
            "issave": "false",
            "guid": guid
        }
        res = self.session.post(url=login_url, headers=headers, data=data)
        self.session.get(url=login_url, headers=headers)
        return self.session
    def __save_homework(self):
        if self.data == {}:
            print('无作业')
        else:
            with open('resource/data/homework', 'w', encoding='utf-8') as f:
                json.dump(self.data,f,ensure_ascii=False,indent=4)
    def __gethomework(self,arg:dict):
        courseid = arg['CourseID']
        classid = arg['TClassID']
        getgomework_url = 'https://www.duifene.com/_HomeWork/HomeWorkInfo.ashx'
        headers = {
            "user - agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "x-requested -with": "XMLHttpRequest",
            "referer":"https://www.duifene.com/_HomeWork/PC/StudentHomeWork.aspx",
            "origin":"https://www.duifene.com",
        }
        data = {
            "action":"gethomeworklist",
            "courseid":courseid,
            "classtypeid":"2",
            "classid":classid,
            "refresh":"0"
        }
        re = self.session.post(url = getgomework_url,headers=headers,data=data)
        return eval(str(re.text))
    def __getguid(self):
        guid = ''
        url_home = 'https://www.duifene.com/Home.aspx'
        re = requests.get(url_home)
        html_content = re.text
        soup = BeautifulSoup(html_content, 'html.parser')
        guid_input = soup.find('input', {'id': 'topLogin_hidOnlyId'})
        if guid_input and 'value' in guid_input.attrs:
            guid = guid_input['value']
            return guid
        return guid
    def __getcourse(self):
        getcourse_url = 'https://www.duifene.com/_UserCenter/CourseInfo.ashx'
        headers = {
            "user - agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "x-requested -with": "XMLHttpRequest",
            "referer": "https://www.duifene.com/_UserCenter/PC/CenterStudent.aspx",
            "origin": "https://www.duifene.com",
        }
        data = {
            "action": "getstudentcourse",
            "classtypeid": "2",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        re = self.session.post(url=getcourse_url,headers=headers,data=data)
        # print(re.text)
        return eval(str(re.text))[:course_count]
    def __fetchhomewok(self):
        self.session = self.__login()
        course_list = self.__getcourse()
        course_dict = {}
        for course in course_list:
            homework_list = self.__gethomework(course)
            if homework_list !=[]:
                homework_l = []
                for homework in homework_list:
                    if(homework['Status']==''):
                        homework_dict = {}
                        homework_dict['作业:'] = homework['HWName']
                        temp =homework['EndDate'].replace('\\/',' ').split(' ')
                        time = temp[3].split(':')
                        date =datetime(int(temp[0]),int(temp[1]),int(temp[2]),int(time[0]),int(time[1]),int(time[2]))
                        homework_dict['截止时间:'] = str(date)
                        homework_l.append(homework_dict)
                if homework_l != []:
                    course_dict[course['CourseName']] = homework_l
        return course_dict
    def __fetch(self):
        self.data = self.__fetchhomewok()
        self.__save_homework()
    def get(self):
        self.__fetch()
        homework_data = {}
        with open('./resource/data/homework','r',encoding='utf-8') as f:
            homework_data = json.load(f)
        return homework_data
# cilent = DuifenyiClient(username='aqiang',password='lQ15182312657')
# data = cilent.get()
# print(data)