import os
import csv
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

class CharaAllHandler(BaseHandler):

    def get(self):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
              "dest/master/chara_data.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            charas = list(reader)

        self.write(charas)
