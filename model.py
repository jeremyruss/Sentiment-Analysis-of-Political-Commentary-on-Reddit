import json
import pickle
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

from kerastuner.tuners import RandomSearch
from kerastuner.engine.hyperparameters import HyperParameters

LOG_DIR = "tuner"

TRAIN_SIZE = 1600
NUM_WORDS = 10000
MAX_LEN = 64

with open('training_data.json', 'r', errors='ignore') as f:
    datastore = json.load(f)

training_data = []
labels = []

for item in datastore:
    training_data.append(item['title'])
    labels.append(item['label'])

train_sentences = training_data[0:TRAIN_SIZE]
test_sentences = training_data[TRAIN_SIZE:]
train_labels = labels[0:TRAIN_SIZE]
test_labels = labels[TRAIN_SIZE:]

tokenizer = Tokenizer(num_words=NUM_WORDS, oov_token="<OOV>")
tokenizer.fit_on_texts(train_sentences)

train_sequences = tokenizer.texts_to_sequences(train_sentences)
test_sequences = tokenizer.texts_to_sequences(test_sentences)

x_train = pad_sequences(train_sequences, maxlen=MAX_LEN, padding='post', truncating='post')
x_test = pad_sequences(test_sequences, maxlen=MAX_LEN, padding='post', truncating='post')

x_train = np.array(x_train)
x_test = np.array(x_test)
y_train = np.array(train_labels)
y_test = np.array(test_labels)

################################################################################

def tuner_model(hp):

    model = tf.keras.Sequential()

    model.add(layers.Embedding(NUM_WORDS,
                               hp.Int('embed_units', min_value=32, max_value=256, step=32),
                               input_length=MAX_LEN))

    for i in range(hp.Int('num_lstm_layers', 0, 3)):
        model.add(layers.Bidirectional(layers.LSTM(hp.Int(f"lstm_{i}_units", min_value=16, max_value=256, step=16), return_sequences=True)))

    model.add(layers.Bidirectional(layers.LSTM(hp.Int('lstm_out_units', min_value=16, max_value=256, step=16))))

    for i in range(hp.Int('num_dense_layers', 1, 4)):
        model.add(layers.Dense(hp.Int(f"dense_{i}_units", min_value=16, max_value=128, step=8), activation='relu'))

    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    return model


def tune():

    tuner = RandomSearch(
        tuner_model,
        objective = "val_accuracy",
        max_trials = 100,
        executions_per_trial = 1,
        directory = LOG_DIR,
        project_name='final_year_project'
        )

    tuner.search(x = x_train,
                 y = y_train,
                 epochs = 3,
                 batch_size = 64,
                 validation_data = (x_test, y_test)
                 )

    with open("tuner.pkl", "wb") as f:
        pickle.dump(tuner, f)

    tuner = pickle.load(open("tuner.pkl", "rb"))

    print(tuner.get_best_hyperparameters()[0].values)
    print(tuner.results_summary())
    print(tuner.get_best_models()[0].summary())

# tune()

################################################################################

def build_model():

    model = tf.keras.Sequential()

    # model.add(layers.Embedding(NUM_WORDS, 16, input_length=MAX_LEN))
    # model.add(layers.GlobalAveragePooling1D())
    # model.add(layers.Dense(32, activation='relu'))
    # model.add(layers.Dense(24, activation='relu'))
    # model.add(layers.Dense(1, activation='sigmoid'))

    model.add(layers.Embedding(NUM_WORDS, 192, input_length=MAX_LEN, mask_zero=True))

    model.add(layers.Bidirectional(layers.LSTM(48, return_sequences=True)))
    model.add(layers.Bidirectional(layers.LSTM(64)))

    model.add(layers.Dense(56, activation='relu'))
    model.add(layers.Dropout(0.2))

    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dropout(0.2))

    model.add(layers.Dense(104, activation='relu'))
    model.add(layers.Dropout(0.2))

    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer=tf.keras.optimizers.Adam(lr=1e-3, decay=1e-5),
                  metrics=['accuracy'])

    return model

#build_model()

def queryModel(samples):

    model = load_model('model.h5')

    sequences = tokenizer.texts_to_sequences(samples)

    padded = pad_sequences(sequences, maxlen=MAX_LEN, padding='post', truncating='post')

    scores = model.predict(padded)

    scores = scores.flatten()

    scores = scores.tolist()

    return scores


def saveModel():

    model = build_model()

    model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=3)

    model.save('model.h5')

#saveModel()
