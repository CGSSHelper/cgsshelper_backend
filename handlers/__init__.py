from tornado.web import RequestHandler
import os


class BaseHandler(RequestHandler):

    def write(self, data):
        payload = {"status": self.get_status(), "result": data}
        self.add_header("Api-Version", os.getenv("API_VER", "1.0.0"))
        self.add_header("Access-Control-Allow-Origin", "*")
        super().write(payload)
