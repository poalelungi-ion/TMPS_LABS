import random
import unicodedata
import re
import torch

class NLPModule:
    def __init__(self, pipeline, encoder, decoder, searcher, voc, predefined_phrases):
        self.pipeline = pipeline
        self.encoder = encoder
        self.decoder = decoder
        self.searcher = searcher
        self.voc = voc
        self.predefined_phrases = predefined_phrases
        self.device = 'cpu'
        self.MAX_LENGTH = 10
        self.PAD_token = 0
        self.SOS_token = 1
        self.EOS_token = 2

    def unicode_to_ascii(self, s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        )

    def normalize_string(self, s):
        s = self.unicode_to_ascii(s.lower().strip())
        s = re.sub(r"([.!?])", r" \1", s)
        s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
        s = re.sub(r"\s+", r" ", s).strip()
        return s

    def indexes_from_sentence(self, msg):
        return [self.voc.word2index[word] if word in self.voc.word2index else self.PAD_token for word in msg.split()] + [self.EOS_token]

    def evaluate(self, msg):
        indexes_batch = [self.indexes_from_sentence(msg)]

        leghts = torch.tensor([len(indexes) for indexes in indexes_batch])

        input_batch = torch.LongTensor(indexes_batch).transpose(0, 1)

        input_batch = input_batch.to(self.device)
        leghts = leghts.to(self.device)

        tokens, scores = self.searcher(input_batch, leghts, self.MAX_LENGTH)

        decoded_words = [self.voc.index2word[token.item()] for token in tokens]
        return decoded_words

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