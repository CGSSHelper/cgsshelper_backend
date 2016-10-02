import os
from . import BaseHandler


class MainHandler(BaseHandler):

    def get(self):
        test_info = {"ApiVer": os.getenv(
            "API_VER", "1.0.0"), "Message": "Welcome"}
        self.write(test_info)
