# Importing all needed libraries.
from datetime import datetime

# Defining the Singleton metaclass, that allows to create Singleton classes.
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        # This function creates a new instance of the class if any instance doesn't exists
        # else it just re-construct the object again.
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

# The main class of the whole application. must have only one instance.
class BrainCore(metaclass=Singleton):
    def __init__(self, com_factory, db_manager, nlp_module, subscribers, token, decorator, message_insert_query_factory, user_insert_query_factory):
        self.com_interface = com_factory.create_interface(token)
        self.com_interface = decorator(self.com_interface)
        self.db_manager = db_manager
        self.nlp_module = nlp_module
        self.subscribers = subscribers
        self.offset = None
        self.message_insert_query_factory = message_insert_query_factory
        self.user_insert_query_factory = user_insert_query_factory

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)

    def notify(self, log_type, message):
        for i in range(len(self.subscribers)):
            self.subscribers[i].update(log_type, message)

    def run(self):
        try:
            while True:
                messages, self.offset = self.com_interface.recv(self.offset)

                for message in messages:
                    resp = self.nlp_module.analyse(message['text'])

                    username = self.db_manager.get_username(message['user_id'], message['platform'])
                    self.notify('warning', f"[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}]Incoming message from user_id {message['user_id']}")
                    if username is None:
                        user_insert_query = self.user_insert_query_factory.create_query(
                            {
                                "query-type" : "user-insert",
                                "params" : {
                                    "user_id" : message['user_id'],
                                    "username" : message['username'],
                                    "platform" : message['platform']
                                }
                            }
                        )
                        self.db_manager.insert_user(*user_insert_query.generate_query())
                    message_insert_query = self.message_insert_query_factory.create_query(
                        {
                            "query-type" : "message-insert",
                            "params" : {
                                "chat_id" : message['chat_id'],
                                "text" : message['text'],
                                "classification" : resp['classification'],
                                "response" : resp['response'],
                                "user_id" : message['user_id'],
                                "platform" : message['platform']
                            }
                        }
                    )

                    self.db_manager.insert_message(*message_insert_query.generate_query())

                    self.notify('warning', f"[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}]ChatBot responded with {resp['response']} to the message from user_id {message['user_id']}")
                    self.com_interface.send(resp['response'], message['chat_id'])
        except KeyboardInterrupt:
            self.db_manager.close()