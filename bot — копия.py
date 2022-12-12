import requests

import json
url = "https://patient.simplex48.ru/api/Web/WorkerCells/"
#payload = "{medorg_id:1,\nbranch_id:"+str(bra_id)+",\nworker_id:"+str(work_id)+",\ndoctor_id:"+str(doct_id)+",\ndate_start:'"+str(doct_date)+"',\ndate_end:'"+str(doct_date)+"',\nreception_kind:0}"
payload = "{medorg_id:1,\nbranch_id:1,\nworker_id:8481,\ndoctor_id:87,\ndate_start:'2023-02-13',\ndate_end:'2023-02-13',\nreception_kind:0}"
headers = {"content-type": "application/json"}
print(payload)
response = requests.request("POST", url, data=payload, headers=headers) 
#for workers in response.json():
data = json.loads(response.text)
#print(data)
from typing import List
from typing import Any
from dataclasses import dataclass
import json

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
#print(root.workers)
for worker in root.workers:
    for cell in worker.schedule[0].cells:
        print(cell.time_start)
print(len(worker.schedule[0].cells))