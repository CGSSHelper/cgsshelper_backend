import os
import csv
from . import BaseHandler


class StoryDetailHandler(BaseHandler):

    def get(self, story_id):
        with open(os.path.dirname(__file__) + os.getenv("STATIC_DIR", "/../static/") +
                  "dest/master/story_detail.csv", "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ret = list(
                filter(lambda row: row["id"] == story_id, reader))[0]
        ret["thumbnail_url"] = "/static/story/story_thumbnail_{0}/thumbnail_{0}.png".format(ret["dialog_id"])
        self.write(ret)
