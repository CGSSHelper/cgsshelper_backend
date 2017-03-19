from tornado.web import RequestHandler
import os


class BaseHandler(RequestHandler):
    SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT", "OPTIONS")

    def write(self, data):
        payload = {"status": self.get_status(), "result": data}
        self.add_header("Api-Version", os.getenv("API_VER", "1.0.0"))
        self.add_header("Access-Control-Allow-Origin", "*")
        super().write(payload)

    def options(self, *args):
        self.add_header("Access-Control-Allow-Origin", "*")
        self.add_header("Access-Control-Allow-Headers", "content-type")
        self.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_status(204)
        self.finish()
