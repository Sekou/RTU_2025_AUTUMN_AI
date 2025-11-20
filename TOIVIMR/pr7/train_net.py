#2024, S. Diane, tensorflow/keras neural network example

from random import sample
import tensorflow as tf
import numpy as np

def create_model(ninps, nouts, weights=None):
    #model = tf.keras.Sequential([
        #tf.keras.layers.Dense(units=64, activation='relu', input_shape=[ninps]),
        #tf.keras.layers.Dense(units=64, activation='relu'),
        #tf.keras.layers.Dense(units=nouts)#, activation=tf.nn.softmax
    #])
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(units=64, activation='relu', input_shape=[1, ninps]),
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=nouts, activation=tf.nn.softmax)
    ])
    if weights: model.load_weights(weights)
    return model

def encode_letter(letter, alphabet):
    res=np.zeros(len(alphabet))
    if letter in alphabet:
        res[alphabet.index(letter)]=1
    return res

def decode_letter(sparse_enc, alphabet):
    i=np.argmax(sparse_enc)
    return alphabet[i]

def decode_letter_prob(sparse_enc, alphabet):
    pp=np.array(sparse_enc).flatten()
    pp=pp-min(pp)
    pp=pp/sum(pp)
    return np.random.choice(alphabet, p=pp)

def load_samples(file):
    with open(file, "r") as f:
        txt=f.read()
        alphabet=sorted(list(set(txt)))
        print(f"alphabet = {alphabet}")
        #for l in alphabet: print(encode_letter(l, alphabet))
        
        all_samples=[]
        X_train=[]
        Y_train=[]
        for i in range(1, len(txt)):
            sample_inp = encode_letter(txt[i-1], alphabet)
            sample_out = encode_letter(txt[i], alphabet)
            all_samples.append([sample_inp, sample_out])
            X_train.append([sample_inp])
            #Y_train.append([sample_out])
            Y_train.append(sample_out) #softmax / categorical_crossentropy
    return alphabet, all_samples, np.array(X_train).tolist(), np.array(Y_train).tolist()

def train_net(out_weights_file='weights.h5'):

    _, _, X_train, Y_train=load_samples("detection_history.txt")
    _, _, X_val, Y_val=load_samples("detection_history2.txt")

    ninps=nouts=len(X_train[0][0])
    model=create_model(ninps, nouts)
    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    losses = model.fit(X_train, Y_train,
                       validation_data=(X_val, Y_val),
                       batch_size=1,
                       epochs=50)

    #result=model.predict(np.array([[0.4, 0.4, 0.4]]))
    #print(result)
    model.save_weights(out_weights_file) 
    print("Success!")

if __name__=="__main__":
    train_net()