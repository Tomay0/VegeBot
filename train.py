from vege_learn import TrainingData, TrainingModel, SEQ_LENGTH
from os import path

if __name__ == '__main__':
    name = input("Enter name to train: ")
    dir_ = 'imitate/' + name + "/"

    if not path.exists(dir_ + "data.txt"):
        print("Could not find data.txt for that person")
    else:
        n_epochs = int(input("Enter number of epochs: "))

        # get training data
        data = TrainingData(dir_ + 'data.txt', SEQ_LENGTH)

        model = TrainingModel(data, dir_ + 'model.json', dir_ + 'model.h5')

        model.train(n_epochs)

        # run a quick test
        random_input = data.random_input()

        print(random_input)

        print(model.generate_output(random_input, 600))
