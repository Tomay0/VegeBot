from vege_learn import TrainingData, TrainingModel
from os import path

if __name__ == '__main__':
    name = input("Enter name to train: ")
    dir_ = 'imitate/' + name + "/"

    if not path.exists(dir_ + "data.txt"):
        print("Could not find data.txt for that person")
    else:
        n_epochs = int(input("Enter number of epochs per save: "))
        n_saves = int(input("Enter number of saves: "))

        # get training data
        data = TrainingData(dir_ + 'data.txt', 20)

        model = TrainingModel(data, dir_ + 'model.json', dir_ + 'model.h5')

        for i in range(n_saves):
            model.train(n_epochs)

        # run a quick test
        random_input = data.random_input()

        print(random_input)

        print(model.generate_output(random_input, 600))
