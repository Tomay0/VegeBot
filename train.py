import os

import vege_learn

if __name__ == '__main__':
    user = input("Enter name: ")

    if not os.path.exists('imitate/' + user + '/data_unicode.txt'):
        print('Could not find data_unicode.txt file within directory imitate/' + user)

    num_generations = int(input("Enter number of generations to train for: "))

    # obtain model

    model = vege_learn.Model(user)

    # begin training
    training = model.get_model()

    for i in range(num_generations):
        training.fit(model.X, model.Y, validation_set=0.1, batch_size=128, n_epoch=1, run_id="vegebot")

        training.save(model.dir + "/model.tflearn")
