import json
import tornado.web
from ..dispatcher import Dispatcher
from ..manager import AsyncJSONRPCResponseManager

class TornadoAPI:
    def __init__(self, serialize=json.dumps, deserialize=json.loads):
        self.manager = AsyncJSONRPCResponseManager(
            Dispatcher(),
            serialize=serialize,
            deserialize=deserialize
        )
    
    @property
    def handler(self):
        """Get Tornado Handler"""
        manager = self.manager

        class TornadoJSONRPCHandler(tornado.web.RequestHandler):
            async def post(self):
                self.set_header("Content-Type", "application/json")
                response = await manager.get_payload_for_payload(self.request.body)
                self.write(response)
        
        return TornadoJSONRPCHandler

    def add_class(self, *args, **kwargs):
        return self.manager.dispatcher.add_class(*args, **kwargs)
    
    def add_object(self, *args, **kwargs):
        return self.manager.dispatcher.add_object(*args, **kwargs)

    def add_method(self, *args, **kwargs):
        return self.manager.dispatcher.add_method(*args, **kwargs)
