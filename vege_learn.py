import numpy as np
import tensorflow as tf

from os import path

from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.python.framework import ops

from random import randint

from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.callbacks import LambdaCallback

SEQ_LENGTH = 30
TEMPERATURE = 0.5

all_data = {}

loaded_model_name = None
loaded_model = None


def load_model(user):
    all_data[user] = TrainingData('imitate/' + user + '/data.txt', SEQ_LENGTH)


def imitate_user(user):
    global loaded_model, loaded_model_name
    training_data = all_data[user]

    if loaded_model_name != user:
        ops.reset_default_graph()
        loaded_model_name = user
        loaded_model = TrainingModel(training_data, 'imitate/' + user + '/model.json',
                                     'imitate/' + user + '/model.h5')

    input_data = training_data.random_input()
    output = loaded_model.generate_output(input_data, 600)

    return output


class TrainingData:
    """
    Some training data for an imitation bot.

    Contains the entire text file and all characters
    """

    def __init__(self, filename, seq_length):
        self.seq_length = seq_length
        self.raw_text = open(filename, 'r', encoding='utf-8').read()

        self.chars = sorted(list(set(self.raw_text)))
        self.char_to_int = dict((c, i) for i, c in enumerate(self.chars))

        total_chars = len(self.raw_text)
        num_chars = len(self.chars)

        sentences = []
        next_chars = []
        for i in range(0, total_chars - seq_length, 3):
            sentences.append(self.raw_text[i: i + seq_length])
            next_chars.append(self.raw_text[i + seq_length])

        # reshape the data to be more useful to keras
        self.x = np.zeros((len(sentences), seq_length, num_chars), dtype=np.bool)
        self.y = np.zeros((len(sentences), num_chars), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                self.x[i, t, self.char_to_int[char]] = 1
            self.y[i, self.char_to_int[next_chars[i]]] = 1

    def random_input(self):
        random_index = randint(0, len(self.raw_text) - self.seq_length)

        chars = self.raw_text[random_index: random_index + self.seq_length]
        return chars

    def compile_input(self, chars):
        data_in = np.zeros((1, self.seq_length, len(self.chars)))
        for t, char in enumerate(chars):
            data_in[0, t, self.char_to_int[char]] = 1

        return data_in


class TrainingModel:
    def __init__(self, training_data, model_file, weight_file):
        self.training_data = training_data
        self.model_file = model_file
        self.weight_file = weight_file

        if path.exists(model_file) and path.exists(weight_file):
            # load the model from a file
            json_file = open(model_file, 'r')
            loaded_model_json = json_file.read()
            json_file.close()

            self.model = model_from_json(loaded_model_json)
            self.model.load_weights(weight_file)
        else:
            # create the model
            self.model = Sequential()
            self.model.add(LSTM(128, input_shape=(self.training_data.seq_length, len(self.training_data.chars))))
            self.model.add(Dense(len(self.training_data.chars), activation='softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.01))

        self.save()

        filepath = "weights.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
        reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.2,
                                      patience=1, min_lr=0.00001)
        save_checkpoint = LambdaCallback(on_epoch_end=lambda epoch, logs: self.save())
        self.callbacks_list = [checkpoint, reduce_lr, save_checkpoint]

    def save(self):
        # save the model
        model_json = self.model.to_json()
        with open(self.model_file, 'w') as json_file:
            json_file.write(model_json)
        self.model.save_weights(self.weight_file)

    def train(self, n_epochs):
        self.model.fit(self.training_data.x, self.training_data.y, epochs=n_epochs, batch_size=128, verbose=2,
                       callbacks=self.callbacks_list)

    def get_output(self, chars):
        """
        Single character output
        :param chars: input chars
        :param temperature: Higher temperature = more surprising, lower temperature = more predictable
        :return:
        """

        data_in = self.training_data.compile_input(chars)
        preds = self.model.predict(data_in, verbose=0)[0]
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / TEMPERATURE
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        index = np.argmax(probas)

        result = self.training_data.chars[index]

        return result

    def generate_output(self, in_chars, n_chars):
        current_input = [char for char in in_chars]
        output = ""

        for i in range(n_chars):
            char = self.get_output(current_input)

            output += char
            current_input.pop(0)
            current_input.append(char)

        return output
