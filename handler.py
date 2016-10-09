from handlers.MainHandler import MainHandler
from handlers.EventHandler import EventAllHandler, EventDetailHandler, EventNowHandler, EventNextHandler
from handlers.CardHandler import CardAllHandler, CharaAllHandler
import tornado
import os
import io
from PIL import Image
from tornado.web import StaticFileHandler

class myFileHandler(StaticFileHandler):

    def validate_absolute_path(self, root, absolute_path):
        abspath = super().validate_absolute_path(root, absolute_path)
        if ("png" in abspath) and ("image/webp" in self.request.headers.get("accept")) and (os.stat(abspath).st_size > 500000):
            # return png as webp to reduce size
            try:
                os.stat(abspath.replace("png", "webp"))
            except:
                im = Image.open(abspath).convert("RGB")
                im.save(abspath.replace("png", "webp"), "WEBP", quality=90)
            return abspath.replace("png", "webp")
        else:
            return abspath


endpoints = [
    (r"/", MainHandler),
    (r"/event/all", EventAllHandler),
    (r"/event/(\d{4})", EventDetailHandler),
    (r"/event/now", EventNowHandler),
    (r"/event/next", EventNextHandler),
    (r"/card/all", CardAllHandler),
    (r"/chara/all", CharaAllHandler),
    (r'/static/(.*)', myFileHandler, {'path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/dest/')}),
]
