import logging

class SubscriberInterface:
    def __init__(self):
        logging.basicConfig()
        self.mapper = {
            "bebug" : logging.debug,
            "info" : logging.info,
            "warning" : logging.warning,
            "error" : logging.error,
            "critical" : logging.critical
        }

    def update(self, log_type, context):
        pass

class LoggerSubscriber(SubscriberInterface):
    def __init__(self):
        super(LoggerSubscriber, self).__init__()

    def update(self, log_type, context):
        self.mapper[log_type](context)

class LogFileSubscriber(SubscriberInterface):
    def __init__(self, filename):
        self.filename = filename
        self.loger = logging.getLogger("file_loger")
        self.fh = logging.FileHandler(filename)
        self.loger.addHandler(self.fh)
        super(LogFileSubscriber, self).__init__()

    def update(self, log_type, context):
        self.loger.warning(context)