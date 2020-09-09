from vege_learn import TrainingData, TrainingModel, SEQ_LENGTH
from os import path, listdir


def train(d, epochs):
    # get training data
    data = TrainingData(d + 'data.txt', SEQ_LENGTH)

    model = TrainingModel(data, d + 'model.json', d + 'model.h5')

    model.train(epochs)

    # run a quick test
    random_input = data.random_input()

    print(random_input)

    print(model.generate_output(random_input, 600))


if __name__ == '__main__':
    name = input("Enter name to train: ")
    dir_ = 'imitate/' + name + "/"

    if not path.exists(dir_ + "data.txt"):
        if name == 'all':
            n_epochs = int(input("Enter number of epochs: "))
            if path.exists('imitate'):
                for user in listdir('imitate'):
                    train('imitate/' + user + "/", n_epochs)
        else:
            print("Could not find data.txt for that person")
    else:
        n_epochs = int(input("Enter number of epochs: "))
        train(dir_, n_epochs)
