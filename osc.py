from asyncio import get_event_loop
from pythonosc import dispatcher, osc_server


class OSCServer:
    def __init__(self, handler, port=5005, ip="0.0.0.0"):
        self.addr = (ip, port)
        self.dispatcher = dispatcher.Dispatcher()
        #for k, v in handlers.items():
        #    if k[0] == '/':
        #        addr = k
        #    else:
        #        addr = '/' + k
        #    self.dispatcher.map(addr, v)
        self.dispatcher.set_default_handler(handler)
        loop = get_event_loop()
        self.server = osc_server.AsyncIOOSCUDPServer(self.addr,
                                                     self.dispatcher,
                                                     loop)
        self.server.serve()

    # def start(self):
    #     if not self.server:
    #         thread = Thread(target=self.server.serve_forever)
    #         thread.start()

    # def stop(self):
    #     if self.server:
    #         self.server.shutdown()
    #         self.server = None
