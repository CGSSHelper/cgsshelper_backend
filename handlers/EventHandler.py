import os
import csv
from datetime import datetime
from pytz import timezone
from . import BaseHandler

types = ["", "Atapon", "Caravan", "Medley", "Party", "Tour"]

class EventAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/event_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            events = []
            for row in reader:
                events.append(row)
            self.write(events)


class EventDetailHandler(BaseHandler):

    def get(self, event_id):
        event = getEventCommData(event_id)
        if(event["comm_data"] == {}):
            self.write(event)
            return

        event["detail"] = {}
        event["detail"]["available"] = getDataFromCSV("event_available", event_id)
        self.write(event)


class EventNowHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/event_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            event = {}
            localtime_japan = datetime.now(timezone('Asia/Tokyo'))
            for row in reader:
                print(row)
                if(timezone('Asia/Tokyo').localize(datetime.strptime(row["event_start"], "%Y-%m-%d %H:%M:%S")) < localtime_japan and
                   timezone('Asia/Tokyo').localize(datetime.strptime(row["result_end"], "%Y-%m-%d %H:%M:%S")) > localtime_japan and not "2099" in row["result_end"]):
                    event_id = row["id"]
        try:
            event = getEventCommData(event_id)
        except NameError:
            self.write({"comm_data": {}})
            return

        if(event["comm_data"]["type"] == "Caravan"):
            # caravan event
            event["caravan"] = {
                "daily_bonus": getDataFromCSV("caravan_data", event_id),
                "detail": getDataFromCSV("caravan_detail", event_id)
            }

        if(event["comm_data"]["type"] == "Atapon"):
            # atapon event
            event["atapon"] = {
                "story_detail": getDataFromCSV("atapon_story_detail", event_id),
                "live_detail": getDataFromCSV("atapon_detail", event_id),
                "point_rank": {
                    "disp": getDataFromCSV("atapon_point_rank_disp", event_id),
                    "reward": getDataFromCSV("atapon_point_rank_reward", event_id)
                },
                "score_rank": {
                    "disp": getDataFromCSV("atapon_score_rank_disp", event_id),
                    "reward": getDataFromCSV("atapon_score_rank_reward", event_id)
                },
                "point_reward": getDataFromCSV("atapon_point_reward", event_id)
            }

        if(event["comm_data"]["type"] == "Medley"):
            # medley event
            event["medley"] = {
                "define": getDataFromCSV("medley_data", event_id),
                "detail": getDataFromCSV("medley_detail", event_id),
                "point_reward": getDataFromCSV("medley_point_reward", event_id),
                "score_rank": {
                    "disp": getDataFromCSV("medley_score_rank_disp", event_id),
                    "reward": getDataFromCSV("medley_score_rank_reward", event_id)
                },
                "point_rank": {
                    "disp": getDataFromCSV("medley_point_rank_disp", event_id),
                    "reward": getDataFromCSV("medley_point_rank_reward", event_id)
                },
                "story_detail": getDataFromCSV("medley_story_detail", event_id)
            }

        if(event["comm_data"]["type"] == "Party"):
            # party event
            event["party"] = {
                "define": getDataFromCSV("party_data", event_id),
                "detail": getDataFromCSV("party_detail", event_id),
                "point_reward": getDataFromCSV("party_point_reward", event_id)
            }

        if(event["comm_data"]["type"] == "Tour"):
            # tour (parade) event
            event["tour"] = {
                "define": getDataFromCSV("tour_data", event_id),
                "point_reward": getDataFromCSV("tour_point_reward", event_id),
                "score_rank": {
                    "disp": getDataFromCSV("tour_score_rank_disp", event_id),
                    "reward": getDataFromCSV("tour_score_rank_reward", event_id)
                },
                "story_detail": getDataFromCSV("tour_story_detail", event_id)
            }

        self.write(event)

class EventNextHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/event_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            localtime_japan = datetime.now(timezone('Asia/Tokyo'))
            for row in reader:
                if(timezone('Asia/Tokyo').localize(datetime.strptime(row["notice_start"], "%Y-%m-%d %H:%M:%S")) < localtime_japan and
                   "2099" in row["result_end"]):
                    event_id = row["id"]
        try:
            self.write(getEventCommData(event_id))
        except NameError:
            self.write({"comm_data": {}})


def getEventCommData(event_id):
    with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") + "dest/master/event_data.csv", "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        event = {}
        event["comm_data"] = list(filter(lambda row: row["id"] == event_id, reader))[0]
    if("comm_data" not in event):
        return {"comm_data": {}}
    event["comm_data"]["bg_url"] = "/static/card/card_bg_{0}/bg_{0}.png".format(event["comm_data"]["bg_id"])
    event["comm_data"]["notice_start"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["notice_start"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["calc_start"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["calc_start"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["event_end"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["event_end"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["event_start"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["event_start"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["result_start"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["result_start"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["result_end"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["result_end"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["second_half_start"] = timezone('Asia/Tokyo').localize(datetime.strptime(event["comm_data"]["second_half_start"], "%Y-%m-%d %H:%M:%S")).isoformat()
    event["comm_data"]["type"] = types[int(event["comm_data"]["type"])]
    return event

def getDataFromCSV(filename="", event_id=0):
    with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/{}.csv".format(filename), "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ret = list(
            filter(lambda row: row["event_id"] == event_id, reader))
    return ret[0] if len(ret) == 1 else ret
