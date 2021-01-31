import tornado.ioloop
import tornado.web
from ajsonrpc.backend.tornado import JSONRPCTornado

api = JSONRPCTornado()

@api.add_method
async def add(a, b):
    return a + b

def make_app():
    return tornado.web.Application([
        (r"/jsonrpc", api.handler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
