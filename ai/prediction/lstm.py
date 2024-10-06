import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam


def _create_sequences(dataset, window_size):
    X, y = [], []
    for i in range(len(dataset) - window_size):
        X.append(dataset[i:i+window_size])
        y.append(dataset[i+window_size])
    return np.array(X), np.array(y)


def _create_model(window_size, features):
    num_features = len(features)

    model = Sequential()
    model.add(Input(shape=(window_size, num_features)))  # Capa de entrada
    model.add(LSTM(64))         # Capa LSTM sin input_shape
    model.add(Dense(num_features))
    model.compile(optimizer=Adam(learning_rate=1e-4), loss='mse')
    
    return model


def _prepare_data(fuzz_data, features, window_size):
    data_sub = fuzz_data.copy()
    dataset = data_sub[features].values
    X, y = _create_sequences(dataset, window_size)

    return X, y


def _train_model(model, X, y):
    
    # División en entrenamiento y prueba
    train_size = int(len(X) * 0.75)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    early_stopping = EarlyStopping(
        monitor='val_loss',               # Métrica a monitorear
        patience=10,                      # Número de épocas sin mejora antes de detener
        verbose=0,                        # Nivel de verbosidad
        mode='min',                       # Minimizar val_loss
        min_delta=0.0001,                 # Mínimo cambio permitido en la métrica
        restore_best_weights=True         # Restaurar los mejores pesos al finalizar
    )

    model.fit(
        X_train,
        y_train,
        epochs=1000,
        batch_size=1,
        validation_data=(X_test, y_test),
        callbacks=[
            early_stopping
        ]
    )

    return model


def _predict(X, model, window_size, features, num_predictions=12):
    num_features = len(features)

    # Generación de predicciones futuras
    future_predictions = []
    last_sequence = X[-1]

    for _ in range(num_predictions):
        next_pred = model.predict(last_sequence.reshape(1, window_size, num_features))
        future_predictions.append(next_pred[0])
        last_sequence = np.append(last_sequence[1:], next_pred, axis=0)

    fuz_predictions = pd.DataFrame(future_predictions, columns=features)

    return fuz_predictions


def lstm_prediction(fuzz_data, window_size, features):
    X, y = _prepare_data(fuzz_data, features, window_size)
    model = _create_model(window_size, features)
    model = _train_model(model, X, y)

    model.save('model.keras')

    fuz_predictions = _predict(X, model, window_size, features)

    return fuz_predictions

def only_prediction(fuzz_data, window_size, features, num_predictions=12):
    X, _ = _prepare_data(fuzz_data, features, window_size)
    model = tf.keras.models.load_model('model.keras')
    fuz_predictions = _predict(X, model, window_size, features, num_predictions)

    return fuz_predictions