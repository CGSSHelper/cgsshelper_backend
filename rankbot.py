import sys
import os
import hashlib
import json
import asyncio
import pymysql
import subprocess

from static import apiclient

from tornado.options import options, define
from tornado.httpclient import AsyncHTTPClient
from datetime import datetime, timedelta
from pytz import timezone
from dateutil import parser
import tornado.gen

bot = None
RES_VER_PATH = os.path.dirname(os.path.realpath(__file__))+'/static/res_ver'
STATIC_UPDATE_EXEC = os.path.dirname(os.path.realpath(__file__))+'/static/bin/python'
STATIC_UPDATE_SCRIPT = os.path.dirname(os.path.realpath(__file__))+'/static/main.py'

define('debug', default=True, help='enable debug mode')
define('port', default=8888, help='run on this port', type=int)

tornado.options.parse_command_line()

# Connect to the database
connection = pymysql.connect(host=os.getenv("DB_HOST", 'localhost'),
                             user=os.getenv("DB_USERNAME", 'root'),
                             password=os.getenv("DB_PASSWORD", ''),
                             db=os.getenv("DB_DATABASE", 'cgssh'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@tornado.gen.coroutine
def checkcall():
    global bot, eventtype, eventid, data, VERSION
    client = AsyncHTTPClient()
    res = yield client.fetch("http://127.0.0.1:{}/event/now".format(options.port))
    if(res.code is not 200):
        print("Is our server down?")
        return
    data = json.loads(res.body.decode("utf-8"))
    if(data["result"]["comm_data"]):
        diff_time_start = (datetime.now(timezone('Asia/Tokyo')) - (parser.parse(data["result"]["comm_data"]["event_start"]))).total_seconds()
        diff_time_event = (datetime.now(timezone('Asia/Tokyo')) - (parser.parse(data["result"]["comm_data"]["event_end"]))).total_seconds()
        diff_time_result = (datetime.now(timezone('Asia/Tokyo')) - (parser.parse(data["result"]["comm_data"]["result_start"]))).total_seconds()
        eventtype = data["result"]["comm_data"]["type"]
        eventid = data["result"]["comm_data"]["id"]
        VERSION = getVersion()
        
        if(data["result"]["comm_data"]["type"] == 'Party' or data["result"]["comm_data"]["type"] == 'Cavaran'):
            return

        if(not bot):
            botperiod = 15 * 60 * 1000
            bot = tornado.ioloop.PeriodicCallback(main, botperiod)
            
        if((not bot.is_running()) and diff_time_event < 0):
            main()
            bot.start()
        elif(diff_time_event > 0 and diff_time_result < 0):
            bot.stop()
        elif(diff_time_result > 0 and diff_time_result < 600):
            main()
    else:
        res = yield client.fetch("http://127.0.0.1:{}/event/next".format(options.port))
        data2 = json.loads(res.body.decode("utf-8"))
        diff_time_start = (datetime.now(timezone('Asia/Tokyo')) - (parser.parse(data2["result"]["comm_data"]["event_start"].replace('2099','2016')))).total_seconds()
        if (not data and not data2):
            VERSION = getVersion()
            main()
        elif(bot):
            bot.stop()


def getVersion():
    try:
        open(RES_VER_PATH, 'r')
    except:
        with open(RES_VER_PATH, 'w') as f:
            f.write('10019960')

    with open(RES_VER_PATH, 'r') as f:
        return f.read()
        
@tornado.gen.coroutine
def call_update():
    user_id, viewer_id, udid = os.getenv("VC_ACCOUNT", "::").split(":")
    client = apiclient.ApiClient(user_id, viewer_id, udid, VERSION)
    args = {
        "campaign_data": "",
        "campaign_user": 1337,
        "campaign_sign": hashlib.md5(b"All your APIs are belong to us").hexdigest(),
        "app_type": 0,
    }
    response, msg = yield from client.call("/load/check", args, None)
    res_ver = msg.get("data_headers", {}).get("required_res_ver", "-1")
    if res_ver != "-1":
        try:
            subprocess.run([STATIC_UPDATE_EXEC, STATIC_UPDATE_SCRIPT], env=os.environ.copy())
            return 1
        except:
            return 1
    else:
        return 0

@tornado.gen.coroutine
def main():
    if(call_update()):
        # just like a game client
        user_id, viewer_id, udid = os.getenv("VC_ACCOUNT", "::").split(":")
        client = apiclient.ApiClient(user_id, viewer_id, udid, VERSION)
        args = {
            "campaign_data": "",
            "campaign_user": 1337,
            "campaign_sign": hashlib.md5(b"All your APIs are belong to us").hexdigest(),
            "app_type": 0,
        }
        response, msg = yield from client.call("/load/check", args, None)
    args = {
        "live_state": 0,
        "friend_view_time": 1467640563,
        "live_setting": 0,
        "load_state": 0,
        "name_card_view_time": 0,
        "live_detail_id": 0,
        "tutorial_flag": 1000
    }
    response, msg = yield from client.call("/load/index", args, None)
    if(data["result"]["comm_data"]["type"] == 'Medley'):
        yield from getMedleyRank(client, parsePointDisp(), parseScoreDisp())
    elif(data["result"]["comm_data"]["type"] == 'Atapon'):
        yield from getAtaponRank(client, parsePointDisp(), parseScoreDisp())
    elif(data["result"]["comm_data"]["type"] == 'Tour'):
        yield from getTourRank(client, parseScoreDisp())


def parsePointDisp():
    event_type = None
    if(data["result"]["comm_data"]["type"] == 'Medley'):
        event_type = "medley"
    elif(data["result"]["comm_data"]["type"] == 'Atapon'):
        event_type = "atapon"
    elif(data["result"]["comm_data"]["type"] == 'Tour'):
        event_type = "tour"
    if(event_type):
        ret = []
        for rank in data["result"][event_type]["point_rank"]["disp"]:
            ret.append(round(int(rank["rank_max"]) / 10))
        return ret
        
def parseScoreDisp():
    event_type = None
    if(data["result"]["comm_data"]["type"] == 'Medley'):
        event_type = "medley"
    elif(data["result"]["comm_data"]["type"] == 'Atapon'):
        event_type = "atapon"
    elif(data["result"]["comm_data"]["type"] == 'Tour'):
        event_type = "tour"
    if(event_type):
        ret = []
        for rank in data["result"][event_type]["score_rank"]["disp"]:
            ret.append(round(int(rank["rank_max"]) / 10))
        return ret

def getAtaponRank(client, pointdisp, scoredisp):
    args = {}
    rank_level = []
    score_level = []
    response, msg = yield from client.call("/event/atapon/load", args, None)
    for rank in pointdisp:
        args = {
            "ranking_type": 1,
            "page": rank
        }
        response, msg = yield from client.call("/event/atapon/ranking_list", args, None)
        #print("rank:{}\n1st: {}\n2nd: {}\n3rd: {}".format(rank, msg["data"]["ranking_list"][0]["user_info"], msg["data"]["ranking_list"][1]["user_info"], msg["data"]["ranking_list"][2]["user_info"]))
        try:
            rank_level.append(msg["data"]["ranking_list"][9]["score"])
        except IndexError:
            rank_level.append(0)
        
    for rank in scoredisp:
        args = {
            "ranking_type": 2,
            "page": rank
        }
        response, msg = yield from client.call("/event/atapon/ranking_list", args, None)
        try:
            score_level.append(msg["data"]["ranking_list"][9]["score"])
        except IndexError:
            score_level.append(0)
        
    with connection.cursor() as cursor:
        sql = "INSERT INTO `point_score` (`actid`, `level1`, `level2`, `level3`, `level4`, `level5`) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (eventid, rank_level[0], rank_level[1], rank_level[2], rank_level[3], rank_level[4]))
        sql = "INSERT INTO `score_rank` (`event_id`, `level1`, `level2`, `level3`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (eventid, score_level[0], score_level[1], score_level[2]))
    connection.commit()

def getTourRank(client, pointdisp):
    args = {}
    score_level = []
    response, msg = yield from client.call("/event/tour/load", args, None)
    for rank in pointdisp:
        args = {
            "ranking_type": 2,
            "page": rank
        }
        response, msg = yield from client.call("/event/tour/ranking_list", args, None)
        #print("rank:{}\n1st: {}\n2nd: {}\n3rd: {}".format(rank, msg["data"]["ranking_list"][7], msg["data"]["ranking_list"][8], msg["data"]["ranking_list"][9]))
        score_level.append(msg["data"]["ranking_list"][9]["score"])
    with connection.cursor() as cursor:
        sql = "INSERT INTO `score_rank` (`event_id`, `level1`, `level2`, `level3`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (eventid, score_level[0], score_level[1], score_level[2]))
    connection.commit()

def getMedleyRank(client, pointdisp, scoredisp):
    args = {
        "get_effect_info": 1,
    }
    rank_level = []
    score_level = []
    response, msg = yield from client.call("/event/medley/load", args, None)
    for rank in pointdisp:
        args = {
            "ranking_type": 1,
            "page": rank
        }
        response, msg = yield from client.call("/event/medley/ranking_list", args, None)
        #print("rank:{}\n1st: {}\n2nd: {}\n3rd: {}".format(rank, msg["data"]["ranking_list"][0]["user_info"], msg["data"]["ranking_list"][1]["user_info"], msg["data"]["ranking_list"][2]["user_info"]))
        rank_level.append(msg["data"]["ranking_list"][9]["score"])
        
    for rank in scoredisp:
        args = {
            "ranking_type": 2,
            "page": rank
        }
        response, msg = yield from client.call("/event/medley/ranking_list", args, None)
        score_level.append(msg["data"]["ranking_list"][9]["score"])
    with connection.cursor() as cursor:
        sql = "INSERT INTO `point_score` (`actid`, `level1`, `level2`, `level3`, `level4`, `level5`) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (eventid, rank_level[0], rank_level[1], rank_level[2], rank_level[3], rank_level[4]))
        sql = "INSERT INTO `score_rank` (`event_id`, `level1`, `level2`, `level3`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (eventid, score_level[0], score_level[1], score_level[2]))
    connection.commit()

if __name__ == '__main__':
    checkcall()
    tornado.ioloop.PeriodicCallback(checkcall, 15 * 60 * 1000).start()
    tornado.ioloop.IOLoop.current().start()
