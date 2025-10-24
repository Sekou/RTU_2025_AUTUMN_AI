#2024, S. Diane, tensorflow/keras neural network example

import tensorflow as tf
import numpy as np

def createModel():
    model = tf.keras.Sequential([

        tf.keras.layers.Dense(units=64, activation='relu',
                              input_shape=[13]),
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=2)#, activation=tf.nn.softmax
    ])
    return model


def trainNet():
    model=createModel()
    model.summary()

    model.compile(optimizer='adam', loss='mae')

    X_train=[]
    Y_train=[]
    with open("log_parking.txt") as f:
        lines=f.readlines()
        for l in lines:
            tokens=l.split()
            inps=[float(v) for v in tokens[3:]] #x y alpha + lidar
            outs=[float(v) for v in tokens[1:3]] #vx vang
            X_train.append(inps)
            Y_train.append(outs)


    #X_train=[[0,0,0], [0.5, 0.5, 0.5], [1, 1, 1]]
    #Y_train=[[1], [2], [3]]
    #X_val=[[0.1,0.1,0.1], [0.7, 0.7, 0.7], [1.3, 1.3, 1.3]]
    #Y_val=[[1.2], [2.4], [3.6]]

    losses = model.fit(X_train, Y_train,
                       validation_data=(X_train, X_train),
                       batch_size=1,
                       epochs=15)

    result=model.predict(np.array([[0.4, 0.4, 0.4]]))
    print(result)

if __name__=="__main__":
    trainNet()