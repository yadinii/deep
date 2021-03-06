import pickle
from tensorflow.keras import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import *
from tensorflow.keras.losses import *
from tensorflow.keras.metrics import *
from tensorflow.keras.callbacks import *
from tensorflow.keras.initializers import *
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import plot_model

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

DATA_PATH = "./cifar-10-batches-py/"
modelName = "rnnNet"

def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

def show_first_samples(x_train, y_train, labels_name):
    
    for i in range(4):
        imgs = x_train[i]
        img0 = imgs[0]
        img1 = imgs[1]
        img2 = imgs[2]
        i0 = Image.fromarray(img0)
        i1 = Image.fromarray(img1)
        i2 = Image.fromarray(img2)
        img = Image.merge("RGB",(i0,i1,i2))
        plt.imshow(img)
        print(labels_name[y_train[i]])
        plt.show()

def create_model():
    model = Sequential()

    #input shape est (nb_samole, nb_time_step, dim)
    model.add(LSTM(512, input_shape=x_train.shape[1:])) #une type de courche rnn, il y a de fonction activation par default
    model.add(Dropout(0.25))

    model.add(Reshape((2, 256)))

    model.add(LSTM(100))
    model.add(Dropout(0.25))

    model.add(Dense(10))
    model.add(Activation('softmax'))

    model.compile(loss = sparse_categorical_crossentropy,
                  optimizer=Adam(),
                  metrics=['accuracy'])
    
    return model

def load_data():
    data_first = unpickle(DATA_PATH + "data_batch_1")
    data_x = data_first[b'data']
    data_y = data_first[b'labels']
    for i in range(2,6):
        data = unpickle(DATA_PATH + f"data_batch_{i}")
        data_x = np.vstack((data_x, data[b'data']))
        data_y += data[b'labels']
    return data_x, data_y


if __name__ == "__main__":
    x_train, y_train = load_data() #load the train data cifar

    data_test = unpickle(DATA_PATH + "test_batch") # load the test data
    x_val, y_val = data_test[b'data'], data_test[b'labels'] 

    data_info = unpickle(DATA_PATH + "batches.meta") #load the data infos
    labels_name = data_info[b'label_names']


    x_train = x_train / 255.0
    x_val = x_val / 255.0

    
    # x_train = x_train.reshape(-1, 3, 32, 32)
    # x_val = x_val.reshape(-1, 3, 32, 32)

    #show_first_samples(x_train, y_train, labels_name)

    x_train = x_train.reshape(-1, 3, 1024)
    x_val = x_val.reshape(-1, 3, 1024)


    y_train = np.array(y_train)
    y_val = np.array(y_val)

    model = create_model()

    

    print(model.summary())
    plot_model(model, f"{modelName}_log/{modelName}.png")

    history = model.fit(x_train, y_train, validation_data=(x_val, y_val),
                epochs=30,
                batch_size=128,
                callbacks=[
                    EarlyStopping(monitor="val_accuracy", patience=2),
                    TensorBoard(log_dir=f"{modelName}_log", histogram_freq=1)
                    ])
    
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.savefig(f'./{modelName}_log/{modelName}_accuracy.png')
    plt.show()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.savefig(f'./{modelName}_log/{modelName}_loss.png')
    plt.show()
