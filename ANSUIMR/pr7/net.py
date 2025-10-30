#2024, S. Diane, tensorflow/keras neural network example


#для парковки в нейросеть подается:
# поперечное отклонение автомобиля от обочины, угол поворота корпуса,
# значения 20 дальностей лидара с прошлого шага времени
# значения 20 дальностей лидара с текущего шага времени

# нейросеть обучается на нормализованных данных в течение 100 эпох


import tensorflow as tf
import numpy as np

def createModel():
    model = tf.keras.Sequential([

        tf.keras.layers.Dense(units=64, activation='relu',
                              input_shape=[42]),
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
    with open("log.txt") as f:
        lines=f.readlines()

        prev_lidars=[]
        for l in lines:
            tokens=l.split()
            lidars=[float(v)/100 for v in tokens[6:]] 
            if len(prev_lidars)==0: prev_lidars=lidars
            inps=[float(tokens[4])/10, float(tokens[5])] + prev_lidars + lidars #y alpha + lidar #координата x не нужна
            outs=[float(v) for v in tokens[1:3]] #vx vang
            X_train.append(inps)
            Y_train.append(outs)
            prev_lidars=lidars


    #X_train=[[0,0,0], [0.5, 0.5, 0.5], [1, 1, 1]]
    #Y_train=[[1], [2], [3]]
    #X_val=[[0.1,0.1,0.1], [0.7, 0.7, 0.7], [1.3, 1.3, 1.3]]
    #Y_val=[[1.2], [2.4], [3.6]]

    losses = model.fit(X_train, Y_train,
                       validation_data=(X_train, Y_train),
                       batch_size=1,
                       epochs=100)

    #result=model.predict(np.array([
        #[150, 0.00, 200, 200, 200, 200, 200, 200, 68, 74, 105, 119]]))
    #print(result)

    model.save_weights("net.weights.h5")

if __name__=="__main__":
    trainNet()
    