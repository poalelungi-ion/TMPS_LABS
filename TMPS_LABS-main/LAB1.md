**TMPS LAB1 : Creational Desing Patterns**

In this laboratory work I created some modules of a Chat Bot for psychological help using 3 Creational Desing Patterns:

I used the following design patterns for the following modules:
* *Singleton* - The **BrainCore** class - the main module of the Chat Bot.
* *Factory Method* - The **MessageInsertQueryCreator** and **UserInsertQueryCreator** - the factories for **Query** objects.
* *Abstract Factory* - The **InterfaceFactory** class, and it's children - used for interfaces creation.

Let's begin with the *Singleton* example.

Singleton
------
The main property of the Singleton Design Pattern is the fact that each class implemented in this way can have only one instance.

In Python this can be achieved by using a metaclass:
```python
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
```
In the example above we can see that the Singleton class inherits the **type** class, which make it a metaclass.

The private filed ```_instance``` is a dictionary that stores all the instances of the class.

The ```__call__``` function is defined to be called instead of the class constructor. In this function the object doesn't exist it is created using the **type** class, else it is re-constructed using the classes ```__init__``` function, finally it always returns the unique instance of this class.

This class is used as a metaclass for the **BrainCore** class that can be found implemented in the *brain_core.py* file.

Abstract Factory
------
A Chat Bot system needs usually an environment for making exchange of messages. Today we have a lot of messaging applications, each having a unique API.

To make easier the use of different Messaging interfaces by the chatbot was implemented a Interface Factory that creates Interfaces of communication from different platforms keeping for all of them a unique API. 

At the beginning were implemented the **InterfaceFactory** class, that is the *Interface* class for different Interface classes.
```python
# Defining the Interface of the Factories.
class InterfaceFactory:
    def create_interface(self, token):
        pass
```
The ```create_interface``` creates a specific Interface using the passed ```token```.

Let's look at the **TelegramFactory** implementing this interface:
```python
# Definition of the Telegram Interface Factory.
class TelegramFactory(InterfaceFactory):
    def create_interface(self, token):
        return TelegramInterface(token)
```

As you can see the ```create_interface``` is returning a instance of the ```TelegramInterface``` class, that is then used by the chatbot to request and send messages.

All Comunication Interfaces classes are following a class interface - ```CommunicationInterface``` class. It defines 2 methods:
* ```recv (self, offset)``` - used to get all messages after a specific offset.
* ```send (self, text, chat_id)``` - sends the text of ```text``` to the chat with the chat id equal to ```chat_id```.

The ```CommunicationInterface``` class.
```python
# Definition of the Communication Interface.
class CommunicationInterface:
    def recv(self, offset):
        pass

    def send(self, text, chat_id):
        pass
```

Using the interface above we can create interfaces for different platforms, hers we will look the the **Telegram** examples:
```python
# Definition of the Telegram Interface.
class TelegramInterface(CommunicationInterface):
    def __init__(self, token):
        self.token = token
        self.url = f"https://api.telegram.org/bot{self.token}"

    def recv(self, offset = None):
        url = self.url + "/getUpdates?timeout=100"
        if offset:
            url = url + f"&offset={offset + 1}"
        url_info = requests.get(url)
        data = json.loads(url_info.content)['result']
        messages = []
        if data:
            for item in data:
                offset = item['update_id']
                try:
                    message = item["message"]["text"]
                except:
                    message = None
                if message:
                    messages.append(
                        {
                            "text" : message,
                            "user_id" : item['message']['from']['id'],
                            "chat_id" : item['message']['chat']['id'],
                            "username" : item['message']['from']['last_name'] if 'last_name' in item['message']['from'] else item['message']['from']['first_name'],
                            "platform" : "telegram"
                        }
                    )
        return messages, offset

    def send(self, text, chat_id):
        url = self.url + f'/sendMessage?chat_id={chat_id}&text={text}'
        if text is not None:
            requests.get(url)
```
The ```recv``` function must return a dictionary of the following form:
```json
{
    "text" : "Hi",
    "user_id" : 234453,
    "chat_id" : 356342,
    "username" : "superman",
    "platform" : "telegram"
}
```
That is passed then to the NLP models and the DB manager if the chatbot for processing and storing.

The ```send``` function just sends text as a message in chat.

In the ```main.py``` file a instance of the ```TelegramFactory``` is created. The it is passed to the ```BrainCore``` constructor.
```python
telegram_factory = TelegramFactory()
...
chatbot_brain_core = BrainCore(telegram_factory,
...
```

In the ```BrainCore``` constructor the factory is used to create the ```TelegramInterface``` instance.
```python
self.com_interface = com_factory.create_interface(token)
```

This interface is then whapped in a ```InterfaceDecorator``` that si implemented from the follwing laboratory works.
```python
self.com_interface = decorator(self.com_interface)
```

The Decorated Interface class folows the ```CommunicationInterface``` class interface and can use ```recv``` and ```send``` functions.
```python
messages, self.offset = self.com_interface.recv(self.offset)
...
self.com_interface.send(resp['response'], message['chat_id'])
```

Factory Method
------
Factory Method is a creational design pattern that provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created.

In this application I used this Design Pattern to implement the creation of queries to the data base.

This chatbot can handle 2 types of insert queries:
* Insert User Query.
* Insert Message Query.

For this purpose I created a ```QueryInterface``` class, that is used as interface for the queries above.
```python
class QueryInterface:
    def __init__(self, params, params_order):
        self.params = params
        self.params_order = params_order

    def generate_query(self):
        pass
```
The ```params``` is a dictionary with parameters that must be inserted in the database, and the ```params_order``` is the order in which they should be sent to database.
```generate_query``` returns a tuple that then is sent to the SQLite ORM.

Using the interface above two types of Query classes are created:
```python
class MessageInsertQuery(QueryInterface):
    def generate_query(self):
        param_order = [self.params[param] for param in self.params_order]
        return tuple(param_order)

class UserInsertQuery(QueryInterface):
    def generate_query(self):
        param_order = [self.params[param] for param in self.params_order]
        return tuple(param_order)
```

To easely generate queries a two Query Creators classes are created using the ```QueryCreator``` class a template:
```python
class QueryCreator:
    def __init__(self, order):
        self.order = order

    def create_query(self, json_data):
        pass

class MessageInsertQueryCreator(QueryCreator):
    def create_query(self, json_data):
        if json_data['query-type'] == 'message-insert':
            return MessageInsertQuery(json_data['params'], self.order)
        else:
            raise WrongQueryType("Massage Insert Query can take only queries for inserting messages in Data Base")

class UserInsertQueryCreator(QueryCreator):
    def create_query(self, json_data):
        if json_data['query-type'] == 'user-insert':
            return UserInsertQuery(json_data['params'], self.order)
        else:
            raise WrongQueryType("User Insert Query can take only queries for inserting users in Data Base")
```

A instance for every type of Query Creator are created in the main application:
```python
user_insert_query_creator = UserInsertQueryCreator(['user_id', 'user_name', 'platform'])
message_insert_query_creator = MessageInsertQueryCreator(
    ['chat_id', 'text', 'classification', 'response', 'user_id', 'platform']
)
```
and then they are sent to the ```BrainCore``` class constructor.

In the ```BrainCore.run``` function they are used to aggregate data from messages and the models and create queries that are then sent to the database:
```python
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
```

Conclusion
------
During this laboratory work I implemented 3 Creational Design Patterns: Singleton, Abstract Factory and Factory Method. I used the Singleton pattern to create the main Core of the application, Abstract Facory for generation of the new Messaging interfaces and the Factory Method for creating queries to the database. 