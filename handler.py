from handlers.MainHandler import MainHandler
from handlers.EventHandler import EventAllHandler, EventDetailHandler, EventNowHandler
from handlers.CardHandler import CardAllHandler, CharaAllHandler
import tornado, os

endpoints = [
    (r"/", MainHandler),
    (r"/event/all", EventAllHandler),
    (r"/event/(\d{4})", EventDetailHandler),
    (r"/event/now", EventNowHandler),
    (r"/card/all", CardAllHandler),
    (r"/chara/all", CharaAllHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/dest/')}),
]
