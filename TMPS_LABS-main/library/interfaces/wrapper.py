from .abstract_factory import CommunicationInterface

class NoConnectionError(BaseException):
    pass

class InterfaceDecorator(CommunicationInterface):
    def __init__(self, interface):
        self.wrappee = interface
        self.on = True

    def send(self, text, chat_id):
        if self.on:
            self.wrappee.send(text, chat_id)
        else:
            raise NoConnectionError("The access to the Interface is forbided!")

    def recv(self, offset):
        if self.on:
            return self.wrappee.recv(offset)
        else:
            raise NoConnectionError("The access to the Interface is forbided!")

    def close(self):
        self.on = False

    def open(self):
        self.on = True