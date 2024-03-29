from typing import List
from typing import Any
from dataclasses import dataclass
import json
from datetime import datetime 
from datetime import date
from datetime import timedelta
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests

def normalize_keyboard(array, max_columns)->VkKeyboard:
    keyboard = VkKeyboard(one_time=True)
    i = 0
    row_count = 1
    print("создаю клавиатуру")
    for element in array:
        if row_count >= 9 or i >= 36:
            break
        if i%max_columns == 0 and i > 0:
            keyboard.add_line()
            row_count += 1
            print("\\n")
        keyboard.add_button(element, color=VkKeyboardColor.POSITIVE)
        print("Добавил кнопку", element)
        i+=1
    return keyboard

def new_record_doctor_buttons(user_id):
    doclist = "Список доступных врачей:\n"
    url = "https://patient.simplex48.ru/api/Web/allspec/1"
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    i = 1
    if len(response.json()) != 0:
        buttons = []
        for element in response.json():
            buttons.append(str(element["name"]))
    else:
        send_message(user_id, "Доступных врачей для записи нет. Нажмите кнопку ''Отмена'' и попробуйте позже. Для новой записи напишите ''Начать'' в чат.")
    send_message(user_id, "Если в процессе записи что-то пойдет не так, напишите в чат ''Отмена'', а затем ''Начать''.")
    keyboard = normalize_keyboard(buttons, 2)
    keyboard.add_line()
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Выберите необходимого специалиста из списка.", keyboard)

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
    bralist = "Выберите поликлинику:\n"
    url = "https://patient.simplex48.ru/api/Web/clinic/1/"+str(doct_id)
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    i = 1
    count_rows = 1

    if len(response.json()) == 1:
        forms.user_data[user_id]["new_record_form"]["new_record_place"] = response.json()[0]["name"]
        forms.set_current_field(user_id, "new_record_doct_name")
        new_record_doct_name(user_id)
        return

    for element in response.json():
        bralist+=element["name"]+"\n"
    if len(response.json()) != 0:
        buttons = []
        for element in response.json():
            buttons.append(str(element["name"]))
    else:
        send_message(user_id, "Доступных поликлиник для записи нет. Нажмите кнопку ''Отмена'' и попробуйте позже. Для новой записи напишите ''Начать'' в чат.")
    #send_message(user_id, "Если в процессе записи что-то пойдет не так, напишите в чат 'Отмена', а затем 'Начать'")
    keyboard = normalize_keyboard(buttons, 2)
    keyboard.add_line()
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Выберите поликлинику, в которую хотите записаться:", keyboard)

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
    namelist = "Выберите ФИО врача к которому хотите записаться:\n"
    url = "https://patient.simplex48.ru/api/Web/allmedic/1/"+str(bra_id)+"/"+str(forms.user_data[user_id]["new_record_form"]["doct_id"])
    response = requests.request("GET", url)
    keyboard = VkKeyboard(one_time=True)
    #i = 1
    #count_rows = 1
    if len(response.json()) != 0:
        buttons = []
        for element in response.json():
            buttons.append(str(element["name"]))
    else:
        send_message(user_id, "Доступных врачей для записи нет. Нажмите кнопку ''Отмена'' и попробуйте позже. Для новой записи напишите ''Начать'' в чат.")
    #send_message(user_id, "Если что-то пошло не так, напишите в чат 'Отмена', а затем 'Начать'")
    keyboard = normalize_keyboard(buttons, 3)
    keyboard.add_line()
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    '''
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
    '''
    send_message(user_id, "Выберите ФИО врача, к которому хотите записаться:", keyboard)

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
    i=0
    if len(response.json()) != 0:
        buttons = []
        for date in reversed(response.json()):
            if i >= 16:
                break
            print_date = datetime.strptime(date, "%d-%m-%Y")
            print_date = print_date.strftime("%d.%m.%y")
            buttons.append(str(print_date))
            i=i+1
        #print(list(date))
        #send_message(user_id, "Если что-то пошло не так, напишите в чат 'Отмена', а затем 'Начать'")
        keyboard = normalize_keyboard(buttons, 4)
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
        send_message(user_id, "Выберите дату посещения специалиста:", keyboard)
    else:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        send_message(user_id, "Свободных дат для записи нет. Напишите в чат Начать и выберите другого врача, если это необходимо.", keyboard)
            
def new_record_doct_time(user_id):
    bra_id = forms.user_data[user_id]["new_record_form"]["bra_id"]
    doct_id = forms.user_data[user_id]["new_record_form"]["doct_id"]
    doct_date = forms.user_data[user_id]["new_record_form"]["new_record_doct_date"]
    doct_name = forms.user_data[user_id]["new_record_form"]["new_record_doct_name"]
    work_id =  forms.user_data[user_id]["new_record_form"]["work_id"]
    doct_date = datetime.strptime(doct_date, "%d.%m.%y")
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
        if len(worker.schedule[0].cells) != 0:
            buttons = []

            for cell in worker.schedule[0].cells:
                if cell.free == True:
                    buttons.append(cell.time_start)

    if len(buttons) == 0:
        message_str = "Простите, но на этот день больше не проводится запись."
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    else:
        message_str = "Выберите время посещения специалиста:"
        keyboard = normalize_keyboard(buttons, 4 )
        keyboard.add_line()
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)


    '''
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
    '''
    #send_message(user_id, "Если что-то пошло не так, то напишите в чат 'Начать'")
    send_message(user_id, message_str, keyboard)
    
   
    
def new_record_client_name(user_id):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Введите Ваше имя:", keyboard)


def new_record_client_lastname(user_id):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Введите Вашу фамилию:", keyboard)


def new_record_client_middlename(user_id):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Введите Ваше отчество:", keyboard)

def new_record_client_phone(user_id):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Введите Ваш номер телефона без кода страны, например: 9505908070.",keyboard)
    

def new_record_client_birth(user_id):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    send_message(user_id, "Введите дату рождения, в формате ДД.ММ.ГГГГ, например: 01.01.2000.",keyboard) 

def new_record_end(user_id):
    user_data = forms.user_data[user_id]["new_record_form"]
    time_obj =datetime.strptime(user_data["new_record_doct_time"], "%H:%M")
    doct_date = datetime.strptime(user_data["new_record_doct_date"], "%d.%m.%y")
    doctdateconfirm = doct_date.strftime("%d.%m.%Y")
    doct_date = doct_date.strftime("%Y-%m-%d")
    birth_date = datetime.strptime(user_data["new_record_client_birth"], "%d.%m.%Y")
    birthdateconfirm = birth_date.strftime("%d.%m.%Y")
    birth_date = birth_date.strftime("%Y-%m-%d")

    Date=str(doct_date)
    timeInterval= time_obj.strftime("%H:%M") + "-" + (time_obj + timedelta(minutes=20)).strftime("%H:%M")
    Name=user_data["new_record_client_name"]
    Phone=user_data["new_record_client_phone"]
    firstName=user_data["new_record_client_name"]
    middleName=user_data["new_record_client_middlename"]
    lastName=user_data["new_record_client_lastname"]
    birthday= str(birth_date)
    
    answer = f"""
Специальность врача: {str(user_data["new_record_doctor"])},
Медицинское учреждение: {str(user_data["new_record_place"])},
Имя врача: {str(user_data["new_record_doct_name"])},
Дата: {doctdateconfirm},
Время: {timeInterval},
Телефон: {Phone},
Фамилия: {lastName},
Имя: {firstName},
Отчество: {middleName},
Дата рождения: {birthdateconfirm}."""


    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Подтвердить", color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)

    send_message(user_id, answer)
    send_message(user_id, "Проверьте введенные данные. Верна ли введённая информация?", keyboard)


    




#TODO 
def new_record_end_end(message):
    user_data = forms.user_data[message.user_id]["new_record_form"]
    print(user_data)
    time_obj =datetime.strptime(user_data["new_record_doct_time"], "%H:%M")
    time = str({user_data["new_record_doct_time"]})
    time = time[2:]
    l = len(time)
    time = time[:l-2]
    l = len(time)
    buf = time[:l-2]
    print(buf)
    doct_date = datetime.strptime(user_data["new_record_doct_date"], "%d.%m.%y")
    doct_date = doct_date.strftime("%Y-%m-%d")
    birth_date = datetime.strptime(user_data["new_record_client_birth"], "%d.%m.%Y")
    birth_date = birth_date.strftime("%Y-%m-%d")
    print(doct_date)
    print(birth_date)

    print(time_obj.strftime("%H:%M") + "-" + (time_obj + timedelta(minutes=20)).strftime("%H:%M"))

    payload = {
    "MEDORG_ID":1,
    "DOCT_ID":user_data["doct_id"],
    "BRA_ID":user_data["bra_id"],
    "WORK_ID":user_data["work_id"],
    "Date":str(doct_date),
    "timeInterval": time_obj.strftime("%H:%M") + "-" + (time_obj + timedelta(minutes=20)).strftime("%H:%M"),
    "Name":user_data["new_record_client_name"],
    "Phone":user_data["new_record_client_phone"],
    "firstName":user_data["new_record_client_name"],
    "middleName":user_data["new_record_client_middlename"],
    "lastName":user_data["new_record_client_lastname"],
    "birthday": str(birth_date),
    }
    url = "http://patient.simplex48.ru:81/token"
    payloadtoken='grant_type=password&username=vk&password=vkP%40ssw0rd'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '.AspNet.Cookies=tfLCNd98hiJrl7Bz8LogNkISEZtEtVaatGCh3M4AMOHCUidovrYoJPakcl0K9a92CmBGE1KUKaAmAlSLvmYoCS5gq3Omi3F465b8qGtV2TyFCZYSWeiwZgJiAtHXMk2UIJh-YWaxWg6RA5IVGIDkyyseuBIYotkH4w-7cIpbXgti4Sz7BxIws0THSwqbRJWNAuCydEJ01x3bbDPD6grtTNzFfUiZfC_llRuD1k7WkymsXSFrwukR4hXrh5ALlFFacaaZxHyF2701TAhCq-bc0daLjXeNGFzez1ye6GbSFnkvziCuuLXDb6i0npYWUGREbbkNnrZyrU1umTUGfRhlLkR9PJcv8U3-yj-B4SEU9dHiitp8-jkhhJGdtZk64FXm7Gi3A2hs7qq5P-kdSv9f2nat-5zjC07c0ds2bIXEBwsHpkyfD0s9cQ4k0dxqdZMPKXEfFjDX1xLAz4qgqkfPWQ'
    }
    response = requests.request("POST", url, headers=headers, data=payloadtoken)
    #print(response.text)
    access_token = response.json()["access_token"]
    #send_message(message.user_id, str(payload))
    url = "http://patient.simplex48.ru:81/api/Web/recordVK"
    payload = json.dumps(payload, indent=1)
    print(payload)
    headers = {"content-type": "application/json", "Authorization" : "Bearer " + str(access_token)}
    response = requests.request("POST", url, data=payload, headers=headers)
    #send_message(message.user_id, str(response.text))
    print(response.text)
    message_data = {
        "Вы записались на прием к врачу: "+str(user_data["new_record_doctor"])+','
        +"\nВ медицинское учреждение: "+str(user_data["new_record_place"])+','
        +"\nК врачу: "+str(user_data["new_record_doct_name"])+','
        +"\nДата приема: "+str(user_data["new_record_doct_date"])+','
        +"\nВремя приема: "+str(user_data["new_record_doct_time"])+'.'
    }
    if response.text != 1:
        url = 'http://patient.simplex48.ru:81/api/Web/confirmationVK/1/'+str(response.text)
        print(url)
        headers = {"content-type": "application/json", "Authorization" : "Bearer " + str(access_token)}
        response = requests.request("GET", url, headers=headers)
        print(response)
        if str(response) == '<Response [200]>':
            send_message(user_id, "Ваша запись успешно создана.")
            send_message(user_id, message_data)
        else:
            send_message(user_id, "Что-то пошло не так. Попробуйте позже.")
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Записаться на приём", color=VkKeyboardColor.POSITIVE)
    send_message(user_id, "Для того, чтобы записаться на прием, напишите в чат ''Начать'', или нажмите на кнопку ''Записаться на прием''.", keyboard)



# API-ключ созданный ранее
token = "vk1.a.xCzAzGn4hP77o3oyPJKlG7xygoNRuanZjHx8TiBOEDf3B4HzdiZbMudpaxrtejqTQAbm9bHTxSRTOomyjW2iBSCebWAC-U9LTidnEbPm-qdEC_g7CMx-ReazzQpZM2UcsroEokrY4OWHJuA2V-7mhmAsXrOS-1lQJmGTwQ6HXXBrpgL6P9q9c3x1OGLBO5G8GBT2XUWX_2B7PhTCMukQng"

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
    "new_record_end_end": new_record_end_end,
}
forms.default_keyboard = VkKeyboard(one_time=True) #Здесь мы создаём дефолтную клавиатуру, которая будет отправляться каждый раз
forms.default_keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
forms.default_keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)

forms.custom_actions = { #Здесь мы делаем словарь, в который вписываем все "custom_action"ы (в нашем случае они делают кнопки)
    "new_record_doctor_buttons":new_record_doctor_buttons,
    "new_record_place_buttons":new_record_place_buttons,
    "new_record_doct_name":new_record_doct_name,
    "new_record_doct_date": new_record_doct_date,
    "new_record_doct_time": new_record_doct_time,
    "new_record_client_lastname": new_record_client_lastname,
    "new_record_client_name": new_record_client_name,
    "new_record_client_middlename": new_record_client_middlename,
    "new_record_client_phone": new_record_client_phone,
    "new_record_client_birth": new_record_client_birth,
    "new_record_end": new_record_end,
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

        if event.text.lower() in ['начать','yfxfnm','отмена','jnvtyf', 'записаться на приём', 'записаться на прием']: #Если написали заданную фразу
            forms.start_form(user_id, "new_record_form")
        else:
           keyboard = VkKeyboard(one_time=True)
           keyboard.add_button("Записаться на приём", color=VkKeyboardColor.POSITIVE)
           send_message(user_id, "Для того, чтобы создать новую запись, напишите в чат ''Начать'', или нажмите на кнопку ''Записаться на приём''.", keyboard) 
