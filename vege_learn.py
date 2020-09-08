import numpy
import tensorflow as tf

from os import path

from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.python.framework import ops

from random import randint

SEQ_LENGTH = 20

all_data = {}


def load_model(user):
    all_data[user] = TrainingData('imitate/' + user + '/data.txt', SEQ_LENGTH)


def imitate_user(user):
    model = TrainingModel(all_data[user], 'imitate/' + user + '/model.json', 'imitate/' + user + '/model.h5')

    output = model.generate_output(model.training_data.random_input(), 600)

    ops.reset_default_graph()

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

        data_x = []
        data_y = []

        for i in range(0, total_chars - seq_length, 1):
            seq_in = self.raw_text[i: i + seq_length]
            seq_out = self.raw_text[i + seq_length]

            # append data as integers
            data_x.append([self.char_to_int[char] for char in seq_in])
            data_y.append(self.char_to_int[seq_out])

        n_patterns = len(data_x)

        # reshape the data to be more useful to keras

        self.x = numpy.reshape(data_x, (n_patterns, seq_length, 1))
        self.x = self.x / float(num_chars)

        self.y = to_categorical(data_y, num_chars)

    def random_input(self):
        random_index = randint(0, len(self.raw_text) - self.seq_length)

        chars = self.raw_text[random_index: random_index + self.seq_length]
        return chars

    def compile_input(self, chars):
        data_in = [self.char_to_int[char] for char in chars]

        data_in = numpy.reshape(data_in, (1, self.seq_length, 1))
        data_in = data_in / float(len(self.chars))

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
            self.model.add(LSTM(256, input_shape=(training_data.x.shape[1], training_data.x.shape[2])))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(training_data.y.shape[1], activation='softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer='adam')

        self.save()

    def save(self):
        # save the model
        model_json = self.model.to_json()
        with open(self.model_file, 'w') as json_file:
            json_file.write(model_json)
        self.model.save_weights(self.weight_file)

    def train(self, n_epochs):
        filepath = "checkpoints/weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]

        self.model.fit(self.training_data.x, self.training_data.y, epochs=n_epochs, batch_size=128,
                       callbacks=callbacks_list)
        self.save()

    def get_output(self, chars):
        """
        Single character output
        :param chars: input chars
        :param temperature: Higher temperature = more surprising, lower temperature = more predictable
        :return:
        """
        data_in = self.training_data.compile_input(chars)
        prediction = self.model.predict(data_in, verbose=0)
        index = numpy.argmax(prediction)

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
