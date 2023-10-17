import pprint
from collections import defaultdict
from datetime import datetime, timedelta
import pprint

data = [
    {
        "CREATED_TIME": "2023-09-29T07:10:27+03:00",
        "STATUS_ID": "NEW"
    },
    {
        "CREATED_TIME": "2023-09-21T07:10:27+03:00",
        "STATUS_ID": "NEW"
    },
    {
        "CREATED_TIME": "2023-09-22T07:10:27+03:00",
        "STATUS_ID": "NEW"
    },
    {
        "CREATED_TIME": "2023-09-23T07:10:27+03:00",
        "STATUS_ID": "PROCESSED"
    },
    {
        "CREATED_TIME": "2023-09-24T07:10:27+03:00",
        "STATUS_ID": "PROCESSED"
    },
    {
        "CREATED_TIME": "2023-09-25T07:10:27+03:00",
        "STATUS_ID": "NEW"
    },
    {
        "CREATED_TIME": "2023-09-20T07:10:27+03:00",
        "STATUS_ID": "NEW"
    },
    {
        "CREATED_TIME": "2023-09-28T07:10:27+03:00",
        "STATUS_ID": "PROCESSED"
    },
    {
        "CREATED_TIME": "2023-09-30T07:10:27+03:00",
        "STATUS_ID": "CONVERTED"
    },
    {
        "CREATED_TIME": "2023-10-03T07:10:27+03:00",
        "STATUS_ID": "CONVERTED"
    }
]

data.sort(key=lambda x: datetime.fromisoformat(x["CREATED_TIME"]))
# pprint.pprint(data)
# first_created_time_on_status = defaultdict(datetime)
first_created_time_on_status = {}
total_time_on_status = defaultdict(timedelta)
previous_record = None
for record in data:
    status_id = record["STATUS_ID"]
    created_time = datetime.fromisoformat(record["CREATED_TIME"])

    # дата попадания на стадию
    if first_created_time_on_status.get(status_id) is None:
        first_created_time_on_status[status_id] = created_time
    elif created_time < first_created_time_on_status[status_id]:
        first_created_time_on_status[status_id] = created_time

    if previous_record is not None:
        time_diff = created_time - datetime.fromisoformat(previous_record["CREATED_TIME"])
        # print(previous_record["STATUS_ID"], " = ", time_diff)
        total_time_on_status[previous_record["STATUS_ID"]] += time_diff

    previous_record = record

# Выведите даты первого попадания CREATED_TIME и суммарное время нахождения на каждой стадии
for status_id, first_time in first_created_time_on_status.items():
    total_time = total_time_on_status[status_id]
    if first_time:
        print(f"Стадия {status_id}:")
        print(f"   Первое попадание CREATED_TIME: {first_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Суммарное время нахождения: {total_time}")
