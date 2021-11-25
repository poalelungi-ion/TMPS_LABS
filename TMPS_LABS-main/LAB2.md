**TMPS LAB2 : Structural Design Patterns**

In this laboratory work I created some modules of a Chat Bot for psychological help using 3 Structural Desing Patterns:

I used the following design patterns for the following modules:
* **Decorator** - Used to create a wrapper around the communication interfaces and to control it's state - implemented as ```InterfaceDecorator``` class.
* **Proxy** - Used to create a wrapper around the Data Base Manager and grant access if possible - implemented as ```DataBaseProxy``` following the ```DataBaseInterface```.
* **Facade** - Used to create the NLP Module for the chatbot that integrates two models: the NLG and NLU model.

Let's begin with the Decorator Design Pattern.

Decorator
------
Decorator is a structural design pattern that lets you attach new behaviors to objects by placing these objects inside special wrapper objects that contain the behaviors.

In this application it is implemented as ```InterfaceDecorator``` class, which wraps around the Interface classes.

The ```InterfaceDecorator``` implements the same functions as all interfaces - ```recv``` and ```send``` calling in their bodies the same function of the wrappee object.

However in this function an additional functionality is added - a test that says if the Interface is on or off. If a function is called when the Interface is off then an error will be raised.
To switch the state of the Decorator there are implemented two functions: 
* ```close``` - turns off the Interface.
* ```open``` - turns on the Interface.

Bellow the whole code is listed:
```python
from interfaces import CommunicationInterface

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
```

In the ```BrainCore``` class constructor this Decorator is used to wrap the telegram interface:
```python
self.com_interface = decorator(self.com_interface)
```

Proxy
------
Proxy is a structural design pattern that lets you provide a substitute or placeholder for another object. A proxy controls access to the original object, allowing you to perform something either before or after the request gets through to the original object.

I use Proxy Design Pattern in this project to control access to the database.

The template of the Database Interface that is used to create the Proxy Pattern implementing class is listed below:
```python
# The DataBaseManager service interface.
class DataBaseInterface:
    def get_username(self, user_id, platform):
        pass

    def get_message_query(self, user_id, platform):
        pass

    def insert_message(self, chat_id, user_msg, classification, response, user_id, platform):
        pass

    def insert_user(self, user_id, user_name, platform):
        pass

    def close(self):
        pass

    def open_access(self):
        pass

    def close_access(self):
        pass
```

Based on it the ```DataBaseProxy``` class is implemented, it takes as an argument a service (DB Manager in this case), and sets the access state to ```True```.
Bellow will be shown only the constructor and a function from this class, the rest of code can be found in the ```proxy.py``` module:
```python
# The Data Base Manager Proxy.
class DataBaseProxy(DataBaseInterface):
    def __init__(self, service):
        self.service = service
        self.access = True

    def get_username(self, user_id, platform):
        if self.access:
            return self.service.get_username(user_id, platform)
        else:
            raise DBNoAccessError("Access isn't granted to the Data Base!")
```

Every function that originally comes from the ```DataBaseManager``` is implemented in the Proxy class. However, before calling the service function it starts with checking the access rights, if Proxy blocks the Data Base Manager then an exception will be generated.

In the main code we are firstly creatting the Data Base Manager, and then we are integrating it in the Proxy:
```python
db_manager = DataBaseManager('database.db')
db_manager_proxy = DataBaseProxy(db_manager)
```
We are sending to the ```BrainCore``` constructor the Proxy of the Data Base Manager. In the ```BrainCore.run``` function it is used to insert messages, users and get usernames:
```python
username = self.db_manager.get_username(message['user_id'], message['platform'])
```

```python
self.db_manager.insert_user(*user_insert_query.generate_query())
```

```python
self.db_manager.insert_message(*message_insert_query.generate_query())
```
Finally in case of the stopping the infinite cycle the Proxy is closing the data base:
```python
except KeyboardInterrupt:
    self.db_manager.close()
```
Facade
------
Facade is a structural design pattern that provides a simplified interface to a library, a framework, or any other complex set of classes.

Usually creating modules that uses Machine Learning and Data Processing means using a lot of libraries, that may be hard for a client to use.

This chatbot has two such modules:
* NLU module - module with submodules for understanding the emotional state of the user.
* NLG module - module wiht submodules for natural language generation.

**NLU module**

NLU (Natural Language Understanding) module is implemented in the ```norm.py``` library. It has the following classes:
* ```TextNormalize``` - This module is used to normalize text.
* ```WordExtractor``` - This module is used to find the hapaxes in a text and then eliminate them with the stopwords at the same time.

The modules above are used to build the emotional state classification pipeline.

**NLG module**

NLG (Natural Language Generation) module is implemented in the ```models.py``` library. It has the following clases:
* **EncoderRNN** - The encoder class used by the Seq-2-Seq model.
* **Attn** - The attention class used by the Seq-2-Seq model.
* **LuongAttnDecoderRNN** - The Loung Attention Decoder class used by the Seq-2-Seq model.
* **GreedySearchDecoder** - The Searcher class used to find the most appropriate toke for a word embedding.
* **Voc** - The vocabulary class that stores the indexes of every token.

**NLP Module**

The functionality of these two modules are combined together in the ```NLPModule``` class.

The main two function that are worth looking at are ```evaluate``` and ```analyse```:

The ```evaluate``` function takes a string and using the models from the NLG submodel generates a new string in form o the list:
```python
def evaluate(self, msg):
    indexes_batch = [self.indexes_from_sentence(msg)]

    leghts = torch.tensor([len(indexes) for indexes in indexes_batch])

    input_batch = torch.LongTensor(indexes_batch).transpose(0, 1)

    input_batch = input_batch.to(self.device)
    leghts = leghts.to(self.device)

    tokens, scores = self.searcher(input_batch, leghts, self.MAX_LENGTH)

    decoded_words = [self.voc.index2word[token.item()] for token in tokens]
    return decoded_words
```

The ```analyse``` function takes a string that is representing the user message and firstly is using the NLU module to classify it. The if the class of the message is ```'normal'``` then it the ```evaluate``` function is used to create a response. If not the from the predifined phrases for every class a random on is taken and is sent used as a response.
This function returns a dictionary with the classification of the text, and the generated response:
```python
def analyse(self, text):
    prediction = self.pipeline.predict([text])[0]
    if prediction == 'normal':
        msg = self.normalize_string(text)
        output_words = self.evaluate(msg)
        output_words[:] = [x for x in output_words if not (x == 'EOS' or x == 'PAD')]
        response = ' '.join(output_words).replace('.', '')

        return {
            "classification" : prediction,
            "response" : response
        }
    else:
        response = random.choice(self.predefined_phrase[prediction])

        return {
            "classification" : prediction,
            "response" : response
        }
```

The creation of a ```NLPModel``` is a process that takes a lot of setting but it gives a easy interface:
```python
# Loading the predefined phrases.
predefined_phrases = json.load(open('predefined_phrase.json', 'r'))

# Loading the vocabulary.
voc = pickle.load(open('voc.pkl', 'rb'))
attn_model = 'dot'

# Loading the emotional state prediction pipeline.
pipe = pickle.load(open('state_model.pkl', 'rb'))

# Setting up the neural network models.
hidden_size = 500
encoder_n_layers = 2
decoder_n_layers = 2
embedding = nn.Embedding(voc.num_words, hidden_size)
dropout = 0.1

enconder = EncoderRNN(hidden_size, embedding, encoder_n_layers, dropout)
decoder = LuongAttnDecoderRNN(attn_model, embedding, hidden_size, voc.num_words, decoder_n_layers, dropout)

enconder.load_state_dict(torch.load('encoder.pt'))
decoder.load_state_dict(torch.load('decoder.pt'))

searcher = GreedySearchDecoder(enconder, decoder)
searcher.load_state_dict(torch.load('searcher.pt'))

nlp_module_obj = NLPModule(pipe, enconder, decoder, searcher, voc, predefined_phrases)
```
This instance is then sent to the ```BrainCore``` constructor, and in the ```BrainCore.run``` function it is used as follows:
```python
resp = self.nlp_module.analyse(message['text'])
```
The ```resp``` dictionary is then sent to the postprocessing and saving to the data base.

Conclusion
------
During this laboratory work I implemented 3 Creational Design Patterns: Decorator, Proxy and Facade. I used the Decorator pattern to create a wrapper around the Communication Interfaces, Proxy for controlling the access to the Data Base, and the Facade combining the NLP modules in a simple model. 