# system library
import os

# tornado library
import tornado.ioloop
import tornado.web
from tornado.options import options, define

# custom things
import handler

define('debug', default=True, help='enable debug mode')
define('port', default=8888, help='run on this port', type=int)

tornado.options.parse_command_line()

print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/dest/'))


def Server():
    settings = {
        "debug": options.debug
    }
    return tornado.web.Application(handler.endpoints, **settings)

if __name__ == '__main__':
    app = Server()
    app.listen(options.port)
    print("Server start at localhost:{}".format(options.port))
    tornado.ioloop.IOLoop.current().start()
