**TMPS LAB3 : Behavioral Design Patterns**

In this laboratory work I created a module logging module for the chatbot using the Behavioral Design Pattern - **Observer**.

Observer is a behavioral design pattern that lets you define a subscription mechanism to notify multiple objects about any events that happen to the object they’re observing.

Observer
------

In the chatbot I used the Observer pattern to create two subscribers that are getting updates from the ```BrainCore``` module.

Firstly I created the ```SubscriberInterface``` class thas is used to create the subscribers.
```python
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
```

Based on It, I created a Logger - ```LoggerSubscriber``` class that logs the events from the ```BrainCore``` into the console:
```python
class LoggerSubscriber(SubscriberInterface):
    def __init__(self):
        super(LoggerSubscriber, self).__init__()

    def update(self, log_type, context):
        self.mapper[log_type](context)
```

And the second type of subscriber is a File Loger - ```LogFileSubscriber``` class which writes the logs into a .log file.
```python
class LogFileSubscriber(SubscriberInterface):
    def __init__(self, filename):
        self.filename = filename
        self.loger = logging.getLogger("file_loger")
        self.fh = logging.FileHandler(filename)
        self.loger.addHandler(self.fh)
        super(LogFileSubscriber, self).__init__()

    def update(self, log_type, context):
        self.loger.warning(context)
```

In the main module of the application they are created in a list.
```python
subscribers = [
    LoggerSubscriber(),
    LogFileSubscriber('log.log')
]
```

Also, the ```BrainCore``` class takes the role of a publisher too. It implements a couple of function of a publisher too:
```python
def subscribe(self, subscriber):
    self.subscribers.append(subscriber)

def unsubscribe(self, subscriber):
    self.subscribers.remove(subscriber)

def notify(self, log_type, message):
    for i in range(len(self.subscribers)):
        self.subscribers[i].update(log_type, message)
```
The functions are doing the following:
* ```subscribe``` - adds a subscriber to the subscription.
* ```unsubscribe``` - removes a subscriber from the subscription.
* ```notify``` - sends the notification to all subscribers.

An example of notification:
```python
self.notify('warning', f"[{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}]Incoming message from user_id {message['user_id']}")
```

The console logs are looking like this:
```
WARNING:root:[2021-11-17 19:37:21]Incoming message from user_id 532596935
WARNING:file_loger:[2021-11-17 19:37:21]Incoming message from user_id 532596935
WARNING:root:[2021-11-17 19:37:21]ChatBot responded with hi      to the message from user_id 532596935
WARNING:file_loger:[2021-11-17 19:37:21]ChatBot responded with hi      to the message from user_id 532596935
```
while the file logs are like this:
```
[2021-11-17 14:43:59]Incoming message from user_id 532596935
[2021-11-17 14:43:59]ChatBot responded with hi      to the message from user_id 532596935
```

Conclusion
------

During this laboratory work I implemented using the Observer Design Pattern two logging modules: a console and a file logger. They allow the BrainCore to store the main events that are happening in the application.