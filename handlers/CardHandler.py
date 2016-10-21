import os
import csv
import random
import functools
import tornado.escape
from . import BaseHandler


class CardAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list(reader)

        for card in cards:
            card["avatar_url"] = "/static/card/card_{0}_m/card_{0}_m.png".format(card["id"])
            card["full_url"] = "/static/card/card_{0}_xl/card_{0}_xl.png".format(card["id"])
        self.write(cards)

class CardDetailHandler(BaseHandler):

    def get(self, card_id):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            card = list(filter(lambda row: row["id"] == card_id, reader))[0]
        card["avatar_url"] = "/static/card/card_{0}_m/card_{0}_m.png".format(card["id"])
        card["full_url"] = "/static/card/card_{0}_xl/card_{0}_xl.png".format(card["id"])

        self.write(card)

class CardGachaHandler(BaseHandler):

    def post(self):
        params = tornado.escape.json_decode(self.request.body)
        total_chance = functools.reduce(lambda x, y: x + y, params["chance"])
        if total_chance is not 100 or len(params["chance"]) is not 3:
            self.set_status(500)
            self.write({"code": 1, "msg": "Invalid argument"})
            return

        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/card_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list(card for card in list(reader) if (int(card["id"]) % 2))

        # generate random cards
        # TODO: at least one SR(rarity 5)
        gacha_cards = []
        start_rarity = [1, 3]
        for x in range(params["amount"]):
            randnum = random.randint(0, 100)
            rarity = start_rarity[params["type"]]
            for chance in params["chance"]:
                if randnum <= chance:
                    break
                rarity += 2
                randnum -= chance
            print(rarity)
            selection = list(card for card in cards if (int(card["rarity"]) is rarity))
            gacha_cards.append(random.choice(selection))

        self.write(gacha_cards)

class CharaAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/chara_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            charas = list(reader)

        self.write(charas)
