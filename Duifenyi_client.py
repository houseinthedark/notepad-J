import requests
import json
import pickle
from bs4 import BeautifulSoup
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
class DuifenyiClient:
    def __init__(self,username,password):
        self.username=username
        self.password = password
        # 构造重试结构参数
        self.retry_strategy = Retry(
            total=3,
            status_forcelist = [429, 500, 502, 503, 504],
            # method_whitelist=['POST','GET'],不支持该参数
            allowed_methods=['POST','GET'],
            backoff_factor=1
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session = requests.session()
        # 挂载适配器
        self.session.mount('https://www.duifene.com/AppCode/LoginInfo.ashx',self.adapter)
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
        res = self.session.post(url=login_url,headers=headers, data=data)
        self.session.get(url=login_url, headers=headers)
        print("login:",res)
        return self.session
    def __save_homework(self):
        if self.data == {}:
            print('无作业')
        else:
            with open('resource/data/homework', 'w', encoding='utf-8') as f:
                json.dump(self.data[0],f,ensure_ascii=False,indent=4)
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
        print("gethomework:",re)
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
        print("getcourse:",re)
        return eval(str(re.text))
    def __save_course(self):
        with open('./resource/data/course','wb') as f:
            # json.dump(f,self.data[1],ensure_ascii=False,indent=4)
            pickle.dump(self.data[1],f)
    def __fetchhomewok(self):
        self.session = self.__login()
        course_list = self.__getcourse()
        len = 0
        now_date = datetime.now()
        now_year = now_date.year
        now_month = now_date.month
        month = 0
        if now_month in range(3,8):
            month = 1
        elif now_month in range(9,13) or now_month ==1:
            month = 6
        for course in course_list:
            temp = course['CreaterDate'].replace('\\/',' ').split(' ')
            time = temp[3].split(':')
            date = datetime(int(temp[0]),int(temp[1]),int(temp[2]),int(time[0]),int(time[1]),int(time[2]))
            specific_time = datetime(now_year, month, 1, 0, 0, 0)
            if date >= specific_time:
                len+=1
            else:
                break
        print("课程数量：",len)
        course_list = course_list[:len]
        course_dict = [dict({"courseName":f"{course['CourseName']}","className":f"{course['ClassName']}"}) for course in course_list]
        print(course_list)
        homework_dict = {}
        for course in course_list:
            homework_list = self.__gethomework(course)
            if homework_list !=[]:
                homework_l = []
                for homework in homework_list:
                    print(homework)
                    temp_h_dict = {}
                    temp_h_dict['作业:'] = homework['HWName']
                    temp = homework['EndDate'].replace('\\/', ' ').split(' ')
                    time = temp[3].split(':')
                    date = datetime(int(temp[0]), int(temp[1]), int(temp[2]), int(time[0]), int(time[1]), int(time[2]))
                    temp_h_dict['截止时间:'] = str(date)
                    if homework['Status']=='' and date>=now_date:
                        homework_l.append(temp_h_dict)
                if homework_l != []:
                    homework_dict[course['CourseName']] = homework_l
        return homework_dict,course_dict
    def __fetch(self):
        self.data = self.__fetchhomewok()
        self.__save_homework()
        self.__save_course()
    def get(self):
        self.__fetch()
        homework_data = {}
        with open('./resource/data/homework','r',encoding='utf-8') as f:
            homework_data = json.load(f)
        return homework_data
# if __name__=='__main__':
#     cilent = DuifenyiClient(username='aqiang',password='lQ15182312657')
    # cilent.fetch()
    # data = cilent.get()
    # print(data)
