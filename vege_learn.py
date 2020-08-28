import re

import os
import pickle
from six.moves import urllib

import tflearn
from tflearn.data_utils import *
from tensorflow.python.framework import ops

models = {}


class Model:
    def __init__(self, name):
        self.name = name
        self.dir = "immitate/" + name
        self.path = self.dir + "/data.txt"
        self.char_idx_file = self.dir + '/char_idx.pickle'

        with open(self.dir + "/data_unicode.txt", "r", encoding='utf-8') as file:
            text = re.sub("[^a-zA-Z\s]+", "", file.read())

            text = text.replace("\u3000", "")

            file_out = open(self.dir + "/data.txt", "w")
            file_out.write(text)
            file_out.close()

        self.maxlen = 25

        char_idx = None
        if os.path.isfile(self.char_idx_file):
            print('Loading previous char_idx')
            char_idx = pickle.load(open(self.char_idx_file, 'rb'))

        X, Y, self.char_idx = \
            textfile_to_semi_redundant_sequences(self.path, seq_maxlen=self.maxlen, redun_step=3,
                                                 pre_defined_char_idx=char_idx)

        pickle.dump(self.char_idx, open(self.char_idx_file, 'wb'))

        models[name] = self

    def get_model(self):
        g = tflearn.input_data([None, self.maxlen, len(self.char_idx)])
        g = tflearn.lstm(g, 512, return_seq=True)
        g = tflearn.dropout(g, 0.5)
        g = tflearn.lstm(g, 512, return_seq=True)
        g = tflearn.dropout(g, 0.5)
        g = tflearn.lstm(g, 512)
        g = tflearn.dropout(g, 0.5)
        g = tflearn.fully_connected(g, len(self.char_idx), activation='softmax')
        g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                               learning_rate=0.001)

        model = tflearn.SequenceGenerator(g, dictionary=self.char_idx,
                                               seq_maxlen=self.maxlen,
                                               clip_gradients=5.0,
                                               checkpoint_path=self.name)

        model.load(self.dir + "/model.tflearn")

        return model


def has_user(name):
    return name in models


def immitate_user(name):
    model = models[name]

    seed = random_sequence_from_textfile(model.path, model.maxlen)

    seq = model.get_model().generate(600, temperature=1.0, seq_seed=seed)

    ops.reset_default_graph()

    return seq
