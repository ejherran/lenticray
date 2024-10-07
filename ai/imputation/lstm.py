import pandas as pd
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer

def _create_sequences(dataset, window_size):
    X, y = [], []
    for i in range(len(dataset) - window_size):
        X.append(dataset[i:i+window_size])
        y.append(dataset[i+window_size])
    return np.array(X), np.array(y)


def _prepare_data(data_serie, features):
    scaler = StandardScaler()
    scaled_fox = scaler.fit_transform(data_serie[features])
    knn_imputer = KNNImputer(n_neighbors=12, weights='uniform')
    knn_data = pd.DataFrame(knn_imputer.fit_transform(scaled_fox), columns=features)
    return knn_data, scaler


def _create_model(window_size, num_features):
    # Construcción del modelo con capa Input explícita
    model = Sequential()
    model.add(Input(shape=(window_size, num_features)))  # Capa de entrada
    model.add(LSTM(512))         # Capa LSTM sin input_shape
    model.add(Dense(num_features))
    model.compile(optimizer=Adam(learning_rate=1e-4), loss='mse')
    return model


def _train_model(model, knn_data, features, window_size):
     # Supongamos que 'data_sub' es el DataFrame con los datos proporcionados
    data_sub = knn_data.copy()

    # Seleccionar las características relevantes
    dataset = data_sub[features].values

    X, y = _create_sequences(dataset, window_size)

    early_stopping = EarlyStopping(
        monitor='loss',                   # Métrica a monitorear
        patience=10,                      # Número de épocas sin mejora antes de detener
        verbose=0,                        # Nivel de verbosidad
        mode='min',                       # Minimizar val_loss
        restore_best_weights=True         # Restaurar los mejores pesos al finalizar
    )

    _h = model.fit(
        X,
        y,
        epochs=1000,
        batch_size=16,
        callbacks=[
            early_stopping
        ]
    )

    return X, model


def _predict_future(X, model, window_size, features, future_predictions_size, scaler):
    # Generación de predicciones futuras
    future_predictions = []
    last_sequence = X[-1]

    for _ in range(future_predictions_size):
        # Realiza la predicción
        next_pred = model.predict(last_sequence.reshape(1, window_size, len(features)))

        # Agrega la predicción a la lista de predicciones futuras
        future_predictions.append(next_pred[0])

        # Actualiza la última secuencia:
        last_sequence = np.append(last_sequence[1:], next_pred, axis=0)

    # Creación del DataFrame con las predicciones
    crazy_predictions = pd.DataFrame(future_predictions, columns=features)
    crazy_predictions[features] = scaler.inverse_transform(crazy_predictions[features])
    return crazy_predictions


def lstm_imputation(data_serie, features, window_size=12):
    knn_data, scaler = _prepare_data(data_serie, features)
    model = _create_model(window_size, len(features))
    X, model = _train_model(model, knn_data, features, window_size)
    crazy_predictions = _predict_future(X, model, window_size, features, data_serie.shape[0], scaler)
    return crazy_predictions