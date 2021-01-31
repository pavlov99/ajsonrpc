from sanic import Sanic
from ajsonrpc.backend.sanic import JSONRPCSanic

app = Sanic("Example App")
api = JSONRPCSanic()
app.route("/jsonrpc", methods=["POST",])(api.handler)

@api.add_function
async def add(a, b):
    return a + b

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
