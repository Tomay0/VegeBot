from vege_learn import TrainingData, TrainingModel, SEQ_LENGTH
from os import path, listdir


def continue_generation():
    name = input("Enter name to generate output for: ")
    dir_ = 'imitate/' + name + "/"

    if not path.exists(dir_ + "data.txt"):
        print("Could not find data.txt for that person")
    else:

        data = TrainingData(dir_ + 'data.txt', SEQ_LENGTH)

        model = TrainingModel(data, dir_ + 'model.json', dir_ + 'model.h5')

        random_input = data.random_input()

        current_input = [char for char in random_input]
        current_line = ""

        while True:
            char = model.get_output(current_input)

            if char == '\n':
                print(current_line)
                current_line = ""
            else:
                current_line += char
            current_input.pop(0)
            current_input.append(char)


if __name__ == '__main__':
    continue_generation()
