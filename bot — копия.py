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


payload={
    'grant_type=password&username=vk&password=vkP@ssw0rd'
}
url = "http://patient.simplex48.ru:81/token"
headers = {"content-type": "application/x-www-form-urlencoded"}
print(payload)
response = requests.request("POST", url, data=payload, headers=headers) 
print(response)