from typing import List
from typing import Any
from dataclasses import dataclass
import json
from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests



def new_record_doctor_buttons(user_id):
    doclist = "Список доступных врачей:\n"
    url = "https://patient.simplex48.ru/api/Web/allspec/1"
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    i = 1
    count_rows = 1
    for element in response.json():
        doclist+=(element["name"])+"\n"
        keyboard.add_button(element["name"],color=VkKeyboardColor.POSITIVE)
        if i < len(response.json()) and i%2 == 0:
            keyboard.add_line()
            count_rows +=1
        i+=1
        if count_rows == 9:
            break
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "К какому врачу из списка желаете записаться.", keyboard)

def new_record_place_buttons(user_id):
    doct_spec = forms.user_data[user_id]["new_record_form"]["new_record_doctor"]
    url = "https://patient.simplex48.ru/api/Web/allspec/1"
    response = requests.request("GET", url)
    doct_id = 0
    for element in response.json():
        if element["name"] == doct_spec:
            doct_id = element["id"]
    forms.user_data[user_id]["new_record_form"]["doct_id"] = doct_id
    print (doct_id)
    bralist = "Выберете Поликлинику:\n"
    url = "https://patient.simplex48.ru/api/Web/clinic/1/"+str(doct_id)
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    i = 1
    count_rows = 1
    for element in response.json():
        bralist+=element["name"]+"\n"
        keyboard.add_button(element["name"], color=VkKeyboardColor.POSITIVE)
        if i < len(response.json()) and i%2 == 0:
            keyboard.add_line()
            count_rows+=1
        i+=1
        if count_rows == 9:
            break
    keyboard.add_line()
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Выберете поликлиннику, в которую хотите записаться:", keyboard)
def new_record_doct_name(user_id):  
    url = "https://patient.simplex48.ru/api/Web/clinic/1/"+str(forms.user_data[user_id]["new_record_form"]["doct_id"])
    response = requests.request("GET", url)  
    bra_name = forms.user_data[user_id]["new_record_form"]["new_record_place"]
    bra_id = 0
    for element in response.json():
        if element["name"] == bra_name:
            bra_id = element["id"]
    forms.user_data[user_id]["new_record_form"]["bra_id"] = bra_id
    print (bra_id)
    namelist = "Выберете ФИО врача к которому хотите записаться:\n"
    url = "https://patient.simplex48.ru/api/Web/allmedic/1/"+str(bra_id)+"/"+str(forms.user_data[user_id]["new_record_form"]["doct_id"])
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    i = 1
    count_rows = 1
    for element in response.json():
        namelist+=element["name"]+"\n"
        keyboard.add_button(element["name"], color=VkKeyboardColor.POSITIVE)
        if i < len(response.json()) and i%2 == 0:
            keyboard.add_line()
            count_rows+-1
        i+=1
        if count_rows == 9:
            break
    keyboard.add_line()
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Выберете ФИО врача, к которому хотите записаться:", keyboard)

def new_record_doct_date(user_id):
    doct_name = forms.user_data[user_id]["new_record_form"]["new_record_doct_name"]

    print(doct_name)
    url = "https://patient.simplex48.ru/api/Web/allmedic/1/"+str(forms.user_data[user_id]["new_record_form"]["bra_id"])+"/"+str(forms.user_data[user_id]["new_record_form"]["doct_id"])
    print(url)
    response = requests.request("GET", url)  
    work_id = 0 #поиск айди врача по по имени
    for element in response.json():
        if element["name"] == doct_name:
            work_id = element["id"]
    forms.user_data[user_id]["new_record_form"]["work_id"] = work_id 
    print (work_id)
    url = "https://patient.simplex48.ru/api/Web/workingdays/1/"+str(forms.user_data[user_id]["new_record_form"]["doct_id"])+"/"+str(forms.user_data[user_id]["new_record_form"]["bra_id"])+"/"+str(work_id)
    response = requests.request("GET", url)
    print (url)
    if len(response.json()) != 0:
        keyboard = VkKeyboard(one_time=True)
        i = 1
        count_rows = 1
        for date in reversed(response.json()):
            keyboard.add_button(date, color=VkKeyboardColor.POSITIVE)
            if i < len(response.json()) and i%3 == 0:
                keyboard.add_line()
                count_rows +=1
            i+=1
            if count_rows == 9:
                break
        keyboard.add_line()
        #print(list(date))
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
        send_message(user_id, "Выберете дату:", keyboard)
    else:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        send_message(user_id, "Свободных дат для записи нет. Напишите в чат Начать и выберете другого врача, если это необходимо", keyboard)
            
def new_record_doct_time(user_id):
    bra_id = forms.user_data[user_id]["new_record_form"]["bra_id"]
    doct_id = forms.user_data[user_id]["new_record_form"]["doct_id"]
    doct_date = forms.user_data[user_id]["new_record_form"]["new_record_doct_date"]
    doct_name = forms.user_data[user_id]["new_record_form"]["new_record_doct_name"]
    work_id =  forms.user_data[user_id]["new_record_form"]["work_id"]
    doct_date = datetime.strptime(doct_date, "%d-%m-%Y")
    doct_date = doct_date.strftime("%Y-%m-%d")
    print(doct_date)
    url = "https://patient.simplex48.ru/api/Web/WorkerCells/"
    payload = "{medorg_id:1,\nbranch_id:"+str(bra_id)+",\nworker_id:"+str(work_id)+",\ndoctor_id:"+str(doct_id)+",\ndate_start:'"+str(doct_date)+"',\ndate_end:'"+str(doct_date)+"',\nreception_kind:0}"
    headers = {"content-type": "application/json"}
    print(payload)
    response = requests.request("POST", url, data=payload, headers=headers) 
    print(response)


    @dataclass
    class Cell:
        id: str
        free: bool
        room: str
        branch_id: int
        date: str
        time_start: str
        time_end: str

        @staticmethod
        def from_dict(obj: Any) -> 'Cell':
            _id = str(obj.get("$id"))
            _free = bool(obj.get("free"))
            _room = str(obj.get("room"))
            _branch_id = int(obj.get("branch_id"))
            _date = str(obj.get("date"))
            _time_start = str(obj.get("time_start"))
            _time_end = str(obj.get("time_end"))
            return Cell(_id, _free, _room, _branch_id, _date, _time_start, _time_end)

    @dataclass
    class Schedule:
        id: str
        worker_id: int
        sched_id: int
        medorg_id: int
        branch_id: int
        doctor_id: int
        cells: List[Cell]
        date: str
        time_begin: str
        time_end: str

        @staticmethod
        def from_dict(obj: Any) -> 'Schedule':
            _id = str(obj.get("$id"))
            _worker_id = int(obj.get("worker_id"))
            _sched_id = int(obj.get("sched_id"))
            _medorg_id = int(obj.get("medorg_id"))
            _branch_id = int(obj.get("branch_id"))
            _doctor_id = int(obj.get("doctor_id"))
            _cells = [Cell.from_dict(y) for y in obj.get("cells")]
            _date = str(obj.get("date"))
            _time_begin = str(obj.get("time_begin"))
            _time_end = str(obj.get("time_end"))
            return Schedule(_id, _worker_id, _sched_id, _medorg_id, _branch_id, _doctor_id, _cells, _date, _time_begin, _time_end)

    @dataclass
    class Worker:
        id: str
        work_id: int
        work_surname: str
        work_name: str
        work_patronimic: str
        reception_duration: int
        schedule: List[Schedule]

        @staticmethod
        def from_dict(obj: Any) -> 'Worker':
            _id = str(obj.get("$id"))
            _work_id = int(obj.get("work_id"))
            _work_surname = str(obj.get("work_surname"))
            _work_name = str(obj.get("work_name"))
            _work_patronimic = str(obj.get("work_patronimic"))
            _reception_duration = int(obj.get("reception_duration"))
            _schedule = [Schedule.from_dict(y) for y in obj.get("schedule")]
            return Worker(_id, _work_id, _work_surname, _work_name, _work_patronimic, _reception_duration, _schedule)

    @dataclass
    class Root:
        id: str
        message: str
        success: bool
        workers: List[Worker]

        @staticmethod
        def from_dict(obj: Any) -> 'Root':
            _id = str(obj.get("$id"))
            _message = str(obj.get("message"))
            _success = bool(obj.get("success"))
            _workers = [Worker.from_dict(y) for y in obj.get("workers")]
            return Root(_id, _message, _success, _workers)

    jsonstring = json.loads(response.text)
    root = Root.from_dict(jsonstring)
    print(response.text)
    
    
    keyboard = VkKeyboard(one_time=True)
    i = 1
    count_rows = 1
    for worker in root.workers:
        for cell in worker.schedule[0].cells:
            if cell.free != 'False':
                keyboard.add_button(cell.time_start, color=VkKeyboardColor.POSITIVE)
            if i < len(worker.schedule[0].cells)  and i%4 == 0:
                keyboard.add_line()
                count_rows+=1
            i+=1
            if count_rows == 9:
                break   
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()     
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Выберете время:", keyboard)   
    
def new_record_client_name(user_id):
    send_message(user_id, "Введите ваше полное имя:")

def new_record_client_lastname(user_id):
    send_message(user_id, "Введите вашу фамилию:")

def new_record_client_middlename(user_id):
    send_message(user_id, "Введите ваше Отчество:")

def new_record_client_phone(user_id):
    send_message(user_id, "Введите ваш номер телефона, начиная с +7:")

def new_record_client_birth(user_id):
    send_message(user_id, "Дату рождения, в формате ГГГГ-ММ-ДД, например 2000-01-01") 

def new_record_end(message):
    send_message(message.user_id, str(forms.user_data[message.user_id]))
    new_record_end_end(message)




#TODO 
def new_record_end_end(message):
    user_data = forms.user_data[message.user_id]["new_record_form"]
    print(user_data)
    
    payload = {
    "medorg_id":1,
    "doct_id":user_data["doct_id"],
    "bra_id":user_data["bra_id"],
    "work_id":user_data["work_id"],
    "date":user_data["new_record_doct_date"],
    "time_interval": str({user_data["new_record_doct_time"]}) + "-" + str({user_data["new_record_doct_time"]}),
    "name":user_data["new_record_client_name"],
    "phone":user_data["new_record_client_phone"],
    "seocode": "вот тут не понял",
    "firstname":user_data["new_record_client_name"],
    "middlename":user_data["new_record_client_middlename"],
    "lastname":user_data["new_record_client_lastname"],
    "birthday": user_data["new_record_client_birth"],
    }
    url = "http://patient.simplex48.ru:81/token"
    payload='grant_type=password&username=vk&password=vkP%40ssw0rd'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '.AspNet.Cookies=tfLCNd98hiJrl7Bz8LogNkISEZtEtVaatGCh3M4AMOHCUidovrYoJPakcl0K9a92CmBGE1KUKaAmAlSLvmYoCS5gq3Omi3F465b8qGtV2TyFCZYSWeiwZgJiAtHXMk2UIJh-YWaxWg6RA5IVGIDkyyseuBIYotkH4w-7cIpbXgti4Sz7BxIws0THSwqbRJWNAuCydEJ01x3bbDPD6grtTNzFfUiZfC_llRuD1k7WkymsXSFrwukR4hXrh5ALlFFacaaZxHyF2701TAhCq-bc0daLjXeNGFzez1ye6GbSFnkvziCuuLXDb6i0npYWUGREbbkNnrZyrU1umTUGfRhlLkR9PJcv8U3-yj-B4SEU9dHiitp8-jkhhJGdtZk64FXm7Gi3A2hs7qq5P-kdSv9f2nat-5zjC07c0ds2bIXEBwsHpkyfD0s9cQ4k0dxqdZMPKXEfFjDX1xLAz4qgqkfPWQ'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    access_token = "XXXTOKENXXX"
    for element in response.json():
        access_token =element["access_token"]
    #send_message(message.user_id, str(payload))
    url = "http://patient.simplex48.ru:81/api/Web/recordDirect/"
    payload = json.dumps(payload, sort_keys=True, indent=1)
    headers = {"content-type": "application/json" "Authorization: Bearer " + str(access_token)}
    response = requests.request("POST", url, data=payload, headers=headers)
    send_message(message.user_id, str(response.text))



# API-ключ созданный ранее
token = "vk1.a.x7aV3LPJu298QH3QD1fyjCsyxgI-he5nUyuzDX9o6-hgPt9viwxQAg2MmtSrl0moPDd-H-vsRriqZAnUNAFViUm2N_R0g7LyIUgcVi3-z1bo83cpv5VCUsYAsi9iXQplqmRUr45BCM6VLm0wflQhhPAylBJjtwe1wkHzUFjqDvPyOOcO5a5DxlMSLp_TmRkv"

# Авторизуемся как сообщество
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
def send_message(user_id, message, keyboard=None):
    post = {
        "user_id":user_id,
        "message":message,
        "random_id":0
    }
    if keyboard !=None:
        post["keyboard"] = keyboard.get_keyboard()
    else:
        post = post
    vk_session.method("messages.send", post)



"""

"""
import forms
forms.send_message = send_message #Здесь мы говорим моему модулю какую именно функцию использовать для отправки сообщения

forms.end_handlers = { #Здесь мы делаем словарь, в который вписываем все "end hanler"ы
    "new_record_end":new_record_end
}
forms.default_keyboard = VkKeyboard(one_time=True) #Здесь мы создаём дефолтную клавиатуру, которая будет отправляться каждый раз
forms.default_keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
forms.default_keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

forms.custom_actions = { #Здесь мы делаем словарь, в который вписываем все "custom_action"ы (в нашем случае они делают кнопки)
    "new_record_doctor_buttons":new_record_doctor_buttons,
    "new_record_place_buttons":new_record_place_buttons,
    "new_record_doct_name":new_record_doct_name,
    "new_record_doct_date": new_record_doct_date,
    "new_record_doct_time": new_record_doct_time,
    "new_record_client_lastname": new_record_client_lastname,
    "new_record_client_name": new_record_client_name,
    "new_record_client_middlename": new_record_client_middlename,
    "new_record_client_phone": new_record_client_phone
}



# Работа с сообщениями
longpoll = VkLongPoll(vk_session)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
    #Слушаем longpoll, если пришло сообщение то:
        user_id = event.user_id
        if forms.is_user_in_form(user_id):
            forms.update(event)
            continue

        if event.text.lower() in ['начать','yfxfnm','отмена','jnvtyf']: #Если написали заданную фразу
            forms.start_form(user_id, "new_record_form")
