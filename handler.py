from handlers.MainHandler import MainHandler
from handlers.EventHandler import EventAllHandler, EventDetailHandler, EventNowHandler, EventNextHandler, EventPointHandler
from handlers.CardHandler import CardAllHandler, CharaAllHandler, CardDetailHandler, CardGachaHandler
from handlers.StoryHandler import StoryDetailHandler
import os
from PIL import Image
from tornado.web import StaticFileHandler


class myFileHandler(StaticFileHandler):

    def validate_absolute_path(self, root, absolute_path):
        abspath = super().validate_absolute_path(root, absolute_path)
        if ("png" in abspath) and ("image/webp" in self.request.headers.get("accept")) and (os.stat(abspath).st_size > 100000):
            # return png as webp to reduce size
            try:
                os.stat(abspath.replace("png", "webp"))
            except:
                im = Image.open(abspath).convert("RGB")
                im.save(abspath.replace("png", "webp"), "WEBP", quality=80)
            return abspath.replace("png", "webp")
        else:
            return abspath
            
    def get_content_type(self):
        if ("webp" in self.absolute_path) and ("image/webp" in self.request.headers.get("accept")):
            # set header to image/webp to prevent download
            return "image/webp"
        return super().get_content_type()


endpoints = [
    (r"/", MainHandler),
    (r"/event/all", EventAllHandler),
    (r"/event/(\d{4})", EventDetailHandler),
    (r"/event/now", EventNowHandler),
    (r"/event/next", EventNextHandler),
    (r"/event/point/(\d{4})", EventPointHandler),
    (r"/card/all", CardAllHandler),
    (r"/card/(\d{6})", CardDetailHandler),
    (r"/card/gacha", CardGachaHandler),
    (r"/chara/all", CharaAllHandler),
    (r"/story/(\d*)", StoryDetailHandler),
    (r'/static/(.*)', myFileHandler,
     {'path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/dest/')}),
]
