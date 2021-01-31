# Examples

### Tornado
```
pip install tornado
```

```python
import tornado.ioloop
import tornado.web
from ajsonrpc.backend.tornado import TornadoAPI

api = TornadoAPI()

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
```

### Sanic
```
pip install sanic
```

```python
from sanic import Sanic
from ajsonrpc.backend.sanic import JSONRPCSanic

app = Sanic("Example App")
api = JSONRPCSanic()
app.route("/jsonrpc", methods=["POST",])(api.handler)

@api.add_method
async def add(a, b):
    return a + b

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```