from typing import List
from typing import Any
from dataclasses import dataclass
import json
from datetime import datetime, date
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests


str = '7-8-2023' 
date_object = datetime.strptime(str, '%d-%m-%Y')
doct_date = date_object.strftime("%Y-%m-%d") 
print(doct_date)
