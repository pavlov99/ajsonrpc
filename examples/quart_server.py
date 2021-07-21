from quart import Quart
from ajsonrpc.backend.quart import JSONRPCQuart

app = Quart("Example App")
app.api = JSONRPCQuart()
app.route("/jsonrpc", methods=["POST",])(app.api.handler)

@app.api.add_function
async def add(a, b):
    return a + b

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
