from library.db import DataBaseManager, DataBaseProxy, MessageInsertQueryCreator, UserInsertQueryCreator
from library.braincore import BrainCore
from library.interfaces import TelegramFactory, InterfaceDecorator
from library.nlp import *
from library.log import LogFileSubscriber, LoggerSubscriber

import pickle
import torch
import torch.nn as nn
import json

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

TOKEN = '1773018605:AAHDuLLLx9NW1f1N7fZIAG1QTzyW8fsKrKQ'

telegram_factory = TelegramFactory()

subscribers = [
    LoggerSubscriber(),
    LogFileSubscriber('log.log')
]

nlp_module_obj = NLPModule(pipe, enconder, decoder, searcher, voc, predefined_phrases)

db_manager = DataBaseManager('database.db')
db_manager_proxy = DataBaseProxy(db_manager)

user_insert_query_creator = UserInsertQueryCreator(['user_id', 'user_name', 'platform'])
message_insert_query_creator = MessageInsertQueryCreator(
    ['chat_id', 'text', 'classification', 'response', 'user_id', 'platform']
)

chatbot_brain_core = BrainCore(telegram_factory,
                               db_manager_proxy,
                               nlp_module_obj,
                               subscribers,
                               TOKEN,
                               InterfaceDecorator,
                               message_insert_query_creator,
                               user_insert_query_creator)

chatbot_brain_core.run()