import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
course_count = 9
def login(username,password):
    login_url = 'https://www.duifene.com/AppCode/LoginInfo.ashx'
    guid = getguid()
    headers = {
        "user - agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "x-requested -with": "XMLHttpRequest",
        "referer": "https://www.duifene.com/Home.aspx",
        "origin": "https://www.duifene.com"
    }
    data = {
        "action": "login",
        "loginname": username,
        "password": password,
        "issave": "false",
        "guid": guid
    }
    s = requests.session()
    res = s.post(url=login_url, headers=headers, data=data)
    s.get(url=login_url, headers=headers)
    print('login:',res)
    # print(res.text)
    return s
def read_homework():
    content = {}
    with open('resource/data/homework', 'r', encoding='utf-8') as f:
        content = json.load(f)
    if content =={}:
        print('homework为空')
    else:
        return content
def save_homework(hl):
    if hl == {}:
        print('无作业')
    else:
        with open('resource/data/homework', 'w', encoding='utf-8') as f:
            json.dump(hl,f,ensure_ascii=False,indent=4)
def gethomework(arg:dict,s):
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
    re = s.post(url = getgomework_url,headers=headers,data=data)
    # print('gethomework:',re)
    return eval(str(re.text))
def getguid():
    guid = ''
    url_home = 'https://www.duifene.com/Home.aspx'
    re = requests.get(url_home)
    html_content = re.text
    soup = BeautifulSoup(html_content, 'html.parser')
    guid_input = soup.find('input', {'id': 'topLogin_hidOnlyId'})
    if guid_input and 'value' in guid_input.attrs:
        guid = guid_input['value']
        # print("GUID:", guid)
        return guid
    # print("GUID:",guid)
    return guid
def getcourse(s):
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
    re = s.post(url=getcourse_url,headers=headers,data=data)
    # print(re.text)
    return eval(str(re.text))[:course_count]
def fetchhomewok(username,password):
    s = login(username,password)
    course_list = getcourse(s)
    course_dict = {}
    for course in course_list:
        homework_list = gethomework(course,s)
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
def fetch(name,pwd):
    data = fetchhomewok(username=name,password=pwd)
    save_homework(data)
