import os
import csv
import random
import heapq
import math
import tornado.escape
from . import BaseHandler


class CardAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list(reader)

        for card in cards:
            card["avatar_url"] = "/static/card/card_{0}_s/card_{0}_s.png".format(card["id"])
            card["full_url"] = "/static/card/card_{0}_xl/card_{0}_xl.png".format(card["id"])
        self.write(cards)


class CardDetailHandler(BaseHandler):

    def get(self, card_id):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            card = list(filter(lambda row: row["id"] == card_id, reader))[0]
        card["avatar_url"] = "/static/card/card_{0}_s/card_{0}_s.png".format(card["id"])
        card["full_url"] = "/static/card/card_{0}_xl/card_{0}_xl.png".format(card["id"])

        self.write(card)


class CardGachaHandler(BaseHandler):

    def post(self):
        '''
        params example:
        {
            "amount": 10,
            "type": 1,
            "probability": [88.5, 10, 1.5],
            "must": true
        }
        TODO: card groups, card filter
        '''

        params = tornado.escape.json_decode(self.request.body)
        total_probability = math.ceil(sum(params["probability"]))
        if total_probability != 100 or len(params["probability"]) is not 3:
            self.set_status(500)
            self.write({"code": 1, "msg": "Invalid argument"})
            return

        def normal_gacha(cards, type, p):
            rarity = [[1, 3, 5], [3, 5, 7], [5, 7]]
            minp, minj = heapq.heappop(p)
            # print((is_must_fulfilled and i == 9) or (is_must_fulfilled or i != 9), is_must_fulfilled, i)
            sel_rarity = rarity[type][minj]
            # minj = minj if (is_must_fulfilled and i == 9) or (is_must_fulfilled or i != 9) else 1
            # is_must_fulfilled = True if sel_rarity > 4 or is_must_fulfilled else False
            selection = list(card for card in cards if (int(card["rarity"]) == sel_rarity))
            result.append(minj)
            heapq.heappush(p, (randoms[minj].normalvariate(
                1. / wtp[minj], 1. / wtp[minj] / 3.) + minp, minj))
            return selection

        def must_gacha(cards):
            probability = [10, 1.5]
            wtp = [1. * x / sum(probability) for x in probability]
            randoms = []
            p = []
            for i, x in enumerate(wtp):
                randoms.append(random)
                p.append((randoms[i].normalvariate(1. / x, 1. / x / 3.), i))
            heapq.heapify(p)
            return normal_gacha(cards, 2, p)

        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list({"id": card["id"], "rarity": card["rarity"]} for card in list(
                reader) if (int(card["id"]) % 2))

        # generate random cards
        # credit: http://huangwei.pro/2015-07/game-random/
        # with in-game probability, the SSR is really super super rare!
        gacha_cards = []
        wtp = [1. * x / sum(params["probability"]) for x in params["probability"]]
        result = []
        randoms = []
        p = []
        for i, x in enumerate(wtp):
            randoms.append(random)
            p.append((randoms[i].normalvariate(1. / x, 1. / x / 3.), i))
        heapq.heapify(p)
        is_must_fulfilled = False if params["must"] else True
        for i in range(params["amount"]):
            print((is_must_fulfilled and i == 9) or (is_must_fulfilled or i != 9), is_must_fulfilled, i)
            if (is_must_fulfilled and i == 9) or (is_must_fulfilled or i != 9):
                selection = normal_gacha(cards, params["type"], p)
                is_must_fulfilled = True if int(selection[0]["rarity"]) > 4 or is_must_fulfilled else False
                gacha_cards.append(random.choice(selection)["id"])
            else:
                selection = must_gacha(cards)
                gacha_cards.append(random.choice(selection)["id"])

        random.shuffle(gacha_cards)
        self.write(gacha_cards)


class CharaAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/chara_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            charas = list(reader)

        self.write(charas)
