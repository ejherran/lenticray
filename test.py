# -*- coding: utf-8 -*-

import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

import io
import enum
import math
import random
import dataclasses
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from dateutil.relativedelta import relativedelta
from sklearn.experimental import enable_iterative_imputer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import IterativeImputer
from sklearn.mixture import GaussianMixture
from sklearn.svm import SVR
from sklearn.metrics import confusion_matrix
import torch
import torch.nn as nn
import torch.optim as optim
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from scipy.stats import pearsonr
from sklearn.impute import KNNImputer
import io
import contextlib
import numpy as np
import pandas as pd

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.optimizers import Adam

from ai.fuzzy import engine
from ai.commons.enums import EutrophicationLevel
from ai.imputation import dual
from ai.prediction import lstm


DATA_ROOT = "/home/admin/project/lenticray/data"
DATA_PATH = f"{DATA_ROOT}/demo"

seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)
torch.manual_seed(seed)

# Si estás usando GPU
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)

# Asegurar comportamiento determinista en cuDNN
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

class TemporalSpace(enum.Enum):
    DAILY = enum.auto()
    WEEKLY = enum.auto()
    MONTHLY = enum.auto()



@dataclasses.dataclass
class Settings:
    temporal_space: TemporalSpace
    target_body: str
    predict_len: int = None

    def __post_init__(self):
        if self.temporal_space == TemporalSpace.MONTHLY:
            self.predict_len = 12
        if self.temporal_space == TemporalSpace.WEEKLY:
            self.predict_len = 52
        if self.temporal_space == TemporalSpace.DAILY:
            self.predict_len = 365

@dataclasses.dataclass
class ModelParameters:
    latent_dim: int = 36
    d_model: int = 128
    nhead: int = 8
    num_layers: int = 4

MAP_LEVELS = {
    EutrophicationLevel.UNKNOWN.value: -np.inf,
    EutrophicationLevel.OLIGOTROPHIC.value: 1,
    EutrophicationLevel.MESOTROPHIC.value: 2,
    EutrophicationLevel.EUTROPHIC.value: 3,
    EutrophicationLevel.HYPEREUTROPHIC.value: 4,
}

VAR_MAPS = {
    "DESCONOCIDO": EutrophicationLevel.UNKNOWN.value,
    "BAJO": EutrophicationLevel.OLIGOTROPHIC.value,
    "MODERADO": EutrophicationLevel.MESOTROPHIC.value,
    "ALTO": EutrophicationLevel.EUTROPHIC.value,
    "MUY ALTO": EutrophicationLevel.HYPEREUTROPHIC.value,
}

def process_data_in_temporal_space(dataset, temporal_space):
    # Copy dataset
    internal_dataset = dataset.copy()

    # Convert 'Sample Date' to datetime format
    internal_dataset['Sample Date'] = pd.to_datetime(internal_dataset['Sample Date'])

    # Process data based on temporal space
    if temporal_space == TemporalSpace.MONTHLY:
        return process_monthly_data(internal_dataset)

    if temporal_space == TemporalSpace.WEEKLY:
        return process_weekly_data(internal_dataset)

    if temporal_space == TemporalSpace.DAILY:
        return process_daily_data(internal_dataset)

def process_monthly_data(internal_dataset):
    # Extract Year and Month from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.year
    internal_dataset['Month'] = internal_dataset['Sample Date'].dt.month

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year and Month, calculating the mean for each group excluding non-numeric columns
        monthly_data = body_data.groupby(['Year', 'Month']).mean(numeric_only=True).reset_index()

        # Create a complete range of months from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min() - relativedelta(months=1)  # Subtract one month from the start date
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per month
        all_months = pd.date_range(start=start_date, end=end_date, freq='MS')
        all_months_df = pd.DataFrame({'Year': all_months.year, 'Month': all_months.month})

        # Merge with the monthly data to ensure all months are represented, filling missing values with NaN
        body_monthly_data = pd.merge(all_months_df, monthly_data, on=['Year', 'Month'], how='left', sort=True)

        # Add the 'Water Body' column
        body_monthly_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_monthly_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Month'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Month']]
    all_data = all_data[columns_order]

    return all_data

def process_weekly_data(internal_dataset):
    # Extract Year and Week from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.isocalendar().year
    internal_dataset['Week'] = internal_dataset['Sample Date'].dt.isocalendar().week

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year and Week, calculating the mean for each group excluding non-numeric columns
        weekly_data = body_data.groupby(['Year', 'Week']).mean(numeric_only=True).reset_index()

        # Create a complete range of weeks from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min() - pd.DateOffset(weeks=1)  # Subtract one week from the start date
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per week (Monday as the start of the week)
        all_weeks = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        all_weeks_df = pd.DataFrame({'Year': all_weeks.isocalendar().year, 'Week': all_weeks.isocalendar().week})

        # Merge with the weekly data to ensure all weeks are represented, filling missing values with NaN
        body_weekly_data = pd.merge(all_weeks_df, weekly_data, on=['Year', 'Week'], how='left', sort=True)

        # Add the 'Water Body' column
        body_weekly_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_weekly_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Week'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Week']]
    all_data = all_data[columns_order]

    return all_data

def process_daily_data(internal_dataset):
    # Extract Year, Month, and Day from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.year
    internal_dataset['Month'] = internal_dataset['Sample Date'].dt.month
    internal_dataset['Day'] = internal_dataset['Sample Date'].dt.day

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year, Month, and Day, calculating the mean for each group excluding non-numeric columns
        daily_data = body_data.groupby(['Year', 'Month', 'Day']).mean(numeric_only=True).reset_index()

        # Create a complete range of days from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min()
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per day
        all_days = pd.date_range(start=start_date, end=end_date, freq='D')
        all_days_df = pd.DataFrame({'Year': all_days.year, 'Month': all_days.month, 'Day': all_days.day})

        # Merge with the daily data to ensure all days are represented, filling missing values with NaN
        body_daily_data = pd.merge(all_days_df, daily_data, on=['Year', 'Month', 'Day'], how='left', sort=True)

        # Add the 'Water Body' column
        body_daily_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_daily_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Month', 'Day'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Month', 'Day']]
    all_data = all_data[columns_order]

    return all_data

def plot_original_vs_model(original_df, imputed_df, features, num_rows=50, labels=['Original', 'Imputed'], x_scale="Months"):
    """
    Función para graficar y comparar los datos originales contra los datos imputados usando seaborn en una sola gráfica.

    Se grafican dos variables por columna, de modo que la cantidad de gráficos varía dependiendo de la cantidad de características.

    :param original_df: DataFrame con los datos originales
    :param imputed_df: DataFrame con los datos imputados
    :param features: Lista de características a comparar (1-8 características)
    :param num_rows: Número de filas a mostrar en la gráfica
    """
    num_features = len(features)
    num_cols = 2
    num_rows_graphs = int(np.ceil(num_features / num_cols))

    fig, axes = plt.subplots(num_rows_graphs, num_cols, figsize=(16, 4 * num_rows_graphs), sharex=True)
    axes = axes.flatten() if num_features > 1 else [axes]

    # Iterar sobre cada característica y graficar
    for idx, feature in enumerate(features):
        ax = axes[idx]

        # Obtener los valores de las características originales y las imputadas
        original_values = original_df[feature].iloc[:num_rows]
        imputed_values = imputed_df[feature].iloc[:num_rows]
        x = np.arange(len(original_values))

        # Crear un DataFrame para los valores originales e imputados
        df_plot = pd.DataFrame({
            x_scale: x,
            labels[0]: original_values.values,
            labels[1]: imputed_values.values
        })

        # Graficar los valores imputados
        sns.lineplot(ax=ax, data=df_plot, x=x_scale, y=labels[1], label=labels[1], color='orange', linestyle='-', linewidth=1.5)

        # Graficar los valores originales solo donde no son NaN
        sns.lineplot(ax=ax, data=df_plot, x=x_scale, y=labels[0], label=labels[0], color='blue', linestyle='--', linewidth=1.5, marker='o')

        # Configuraciones adicionales
        ax.set_title(f"Comparación de {feature}")
        ax.set_xlabel(x_scale)
        ax.set_ylabel(feature)
        ax.legend(loc='upper right')

    # Eliminar gráficos vacíos si no hay suficientes características
    for idx in range(num_features, len(axes)):
        fig.delaxes(axes[idx])

    plt.tight_layout()
    plt.show()

def plot_categorical_comparison(
        real_labels,
        predicted_labels,
        categories=['OLIGOTRÓFICO', 'MESOTRÓFICO', 'EUTRÓFICO', 'HIPEREUTRÓFICO'],
        title="Comparación de Categorías de Eutrofización",
        x_label="CATEGORÍA INFERIDA",
        y_label="CATEGORÍA TSI",
        title_fontsize=14,
        label_fontsize=12,
        tick_label_fontsize=10,
        annotation_fontsize=10,
        figsize=(8, 6)
    ):
    """
    Grafica una matriz de confusión comparando dos listas de categorías.

    Args:
        real_labels (list): Lista de categorías reales.
        predicted_labels (list): Lista de categorías predichas.
        categories (list, opcional): Lista de categorías que se esperan en los datos.
        title (str, opcional): Título del gráfico.
        x_label (str, opcional): Etiqueta del eje X.
        y_label (str, opcional): Etiqueta del eje Y.
        title_fontsize (int, opcional): Tamaño de fuente del título.
        label_fontsize (int, opcional): Tamaño de fuente de las etiquetas de los ejes.
        tick_label_fontsize (int, opcional): Tamaño de fuente de las etiquetas de los ticks.
        annotation_fontsize (int, opcional): Tamaño de fuente de las anotaciones de la matriz.
        figsize (tuple, opcional): Tamaño de la figura en pulgadas.
    """
    # Generar la matriz de confusión
    conf_matrix = confusion_matrix(real_labels, predicted_labels, labels=categories)

    # Crear un DataFrame de la matriz de confusión para facilitar la visualización
    df_conf_matrix = pd.DataFrame(conf_matrix, index=categories, columns=categories)

    # Configurar la visualización con Seaborn
    plt.figure(figsize=figsize)
    ax = sns.heatmap(
        df_conf_matrix,
        annot=True,
        cmap='Blues',
        fmt='d',
        cbar=True,
        xticklabels=categories,
        yticklabels=categories,
        annot_kws={"size": annotation_fontsize}
    )

    # Añadir títulos y etiquetas con los tamaños de fuente especificados
    plt.title(title, fontsize=title_fontsize, fontweight='bold')
    plt.xlabel(x_label, fontsize=label_fontsize)
    plt.ylabel(y_label, fontsize=label_fontsize)

    # Ajustar el tamaño de las etiquetas de los ticks
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=tick_label_fontsize)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=tick_label_fontsize)

    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

def plot_training_history_sns(history, save_path=None):
    """
    Grafica las curvas de pérdida de entrenamiento y validación usando Seaborn.

    Parámetros:
    - history: Objeto History retornado por model.fit().
    - save_path: Ruta donde se guardará la gráfica. Si es None, se mostrará en pantalla.
    """
    # Configurar el estilo de Seaborn
    sns.set(style="whitegrid", palette="muted", color_codes=True)

    # Extraer datos del historial
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(loss) + 1)

    # Crear un DataFrame para facilitar la graficación con Seaborn
    df_loss = pd.DataFrame({
        'Época': epochs,
        'Pérdida de Entrenamiento': loss,
        'Pérdida de Validación': val_loss
    })

    # Transformar el DataFrame a formato largo (long-form) para Seaborn
    df_long = df_loss.melt(id_vars='Época',
                           value_vars=['Pérdida de Entrenamiento', 'Pérdida de Validación'],
                           var_name='Tipo de Pérdida',
                           value_name='Valor')

    # Crear la gráfica usando Seaborn
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=df_long, x='Época', y='Valor', hue='Tipo de Pérdida')

    # Añadir títulos y etiquetas
    plt.title('Curva de Pérdida de Entrenamiento y Validación')
    plt.xlabel('Épocas')
    plt.ylabel('Pérdida (MSE)')
    plt.legend(title='Tipo de Pérdida')

    # Mostrar o guardar la gráfica
    if save_path:
        plt.savefig(save_path)
        print(f"Gráfica guardada en: {save_path}")
    else:
        plt.show()

    # Cerrar la figura para liberar memoria
    plt.close()

samples = pd.read_parquet(f"{DATA_PATH}/samples_refined_water_bodies.parquet")

samples['Water Body'].value_counts()

_config = Settings(
    temporal_space=TemporalSpace.MONTHLY,
    target_body='LAGO MAZAIS BALTEZERS'                                              # 'LAGO KASUMIGAURA', 'LAGO MJOSA', 'LAGO ONTARIO', 'LAGO ESTERO DE MEZCALA', 'LAGO MAZAIS BALTEZERS'
)

target_data = samples[samples['Water Body'] == _config.target_body]
target_data.reset_index(drop=True, inplace=True)

data_date = target_data.copy()
data_date['Sample Date'] = pd.to_datetime(data_date['Sample Date'])
data_date.drop(columns=['Water Body'], inplace=True)

data_group = data_date.groupby('Sample Date').mean().reset_index()

base_columns = [
    "Chl_a",
    "DIN",
    "DKN",
    "NH3N",
    "NH4N",
    "NOxN",
    "NO2N",
    "NO3N",
    "PN",
    "PON",
    "TDN",
    "TKN",
    "TN",
    "TON",
    "DON",
    "DIP",
    "DRP",
    "TDP",
    "TIP",
    "TP",
    "TRP",
    "TPP",
    "BOD",
    "COD",
    "O2_Dis",
    "PV",
    "TDS",
    "TS",
    "TSS",
    "FDS",
    "FS",
    "VDS",
    "VS",
    "TRANS",
    "TURB",
    "TEMP",
    "pH",
]
non_null_columns = data_group.columns[data_group.notna().any()].tolist()
numeric_columns = [col for col in base_columns if col in non_null_columns]

data = data_group[numeric_columns]

# resultados, entradas, errores = engine.ejecutar_motor(data)

# reporte_eveluacion = engine.evaluar_motor(data, resultados)
# print(f"Total de muestras: {reporte_eveluacion.get('reals')}")
# print(f"Inferencias correctas: {reporte_eveluacion.get('exacts')}")
# print(f"Inferencias incorrectas: {reporte_eveluacion.get('fails')}")
# print(f"Precision: {reporte_eveluacion.get('precision')}")
# print(f"Aptitud: {reporte_eveluacion.get('aptitud')}")

# reporte_inferencia = engine.generar_reporte(entradas, resultados)

#print(reporte_inferencia[0])

# tsi = reporte_motor.get('tsi')
# for i, val in enumerate(tsi):
#     print(f"{i}\t{val}")

# plot_categorical_comparison(
#     reporte_eveluacion.get('validacion'),
#     reporte_eveluacion.get('inferencia')
# )

data_serie = target_data.copy()

data_serie = process_data_in_temporal_space(data_serie, TemporalSpace.MONTHLY)

#Ordenar para garantizar el orden temporal

if _config.temporal_space == TemporalSpace.MONTHLY:
    data_serie = data_serie.sort_values(by=['Year', 'Month'])

if _config.temporal_space == TemporalSpace.WEEKLY:
    data_serie = data_serie.sort_values(by=['Year', 'Week'])

if _config.temporal_space == TemporalSpace.DAILY:
    data_serie = data_serie.sort_values(by=['Year', 'Month', 'Day'])

# data_serie = data_serie[numeric_columns + ['Year', 'Month']]

# print("Imputación de datos con GRUD y LSTM...")
# data_serie_filled = dual.dual_imputation(data_serie, numeric_columns)

# # plot_original_vs_model(data_serie, data_serie_filled, ['Chl_a', 'NH3N', 'TP', 'TRANS'], num_rows=crazy_predictions.shape[0], labels=['Original', 'Imputado'])

# print("Ejecución del motor de inferencia difusa...")
# fuz_data_serie, _, _ = engine.ejecutar_motor(data_serie_filled)

# fuz_vars = ['eutrofizacion', 'quimicas', 'fisicas', 'adicionales']
# fuz_data = {
#     'eutrofizacion': [],
#     'quimicas': [],
#     'fisicas': [],
#     'adicionales': []
# }

# for i in fuz_data_serie:
#     for c in fuz_vars:
#         fuz_data[c].append(i[c]['valor'])

# fuz_data = pd.DataFrame(fuz_data)
# fuz_data.info()

# validation_predict = fuz_data.iloc[-1*_config.predict_len:]
# validation_predict.info()

# train_data = fuz_data.iloc[:-1*_config.predict_len]
# train_data.info()

# print(train_data.head())

# validation_predict.to_parquet(f"{DATA_PATH}/validation_predict.parquet")
# train_data.to_parquet(f"{DATA_PATH}/train_data.parquet")

# print("Cargando datos de entrenamiento y validación...")

validation_predict = pd.read_parquet(f"{DATA_PATH}/validation_predict.parquet")
train_data = pd.read_parquet(f"{DATA_PATH}/train_data.parquet")

# print(train_data.head())

# print("Entrenamiento del modelo LSTM...")

features = ['eutrofizacion', 'quimicas', 'fisicas', 'adicionales']
#fuz_predictions = lstm.lstm_prediction(train_data, 12, features)

fuz_predictions = lstm.only_prediction(train_data, 12, features, 12)

print("Predicción de datos futuros...")
for row in fuz_predictions.iterrows():
    print(row)

# _mn = {
#     'eutrofizacion': 'Nivel de Eutrofización',
#     'quimicas': 'Condiciones Químicas',
#     'fisicas': 'Condiciones Físicas',
#     'adicionales': 'Condiciones Adicionales'
# }

# vp = validation_predict.rename(columns=_mn)
# fp = fuz_predictions.rename(columns=_mn)

# plot_original_vs_model(vp, fp, _mn.values(), num_rows=fuz_predictions.shape[0], labels=['Original', 'Predicción'], x_scale="Months")

# originals = []
# predicts = []
# fuzis = []

# for i in range(validation_predict.shape[0]):
#     a = NivelEutrofizacion(validation_predict.iloc[i]['quimicas'], validation_predict.iloc[i]['fisicas'], validation_predict.iloc[i]['adicionales'])
#     a.calcular_inferencia()
#     originals.append(a.obtener_etiqueta())

#     a = NivelEutrofizacion(fuz_predictions.iloc[i]['quimicas'], fuz_predictions.iloc[i]['fisicas'], fuz_predictions.iloc[i]['adicionales'])
#     a.calcular_inferencia()
#     fuzis.append(a.obtener_etiqueta())

#     if i == validation_predict.shape[0]-1:
#         a.nivel_eutrofizacion_var.view(sim=a.simulation)
#         # Ajustar las etiquetas de los ejes
#         fig = plt.gcf()
#         fig.set_size_inches(6, 4)
#         ax = plt.gca()
#         ax.set_xlabel("Nivel de Eutrofización", fontsize=10)
#         ax.set_ylabel("Pertenencia", fontsize=10)

#         # Ajustar la posición de la leyenda
#         ax.legend(loc="upper right", fontsize=8)

#         ax.tick_params(axis='both', which='major', labelsize=8)

#     a = NivelEutrofizacion(0, 0, 0)
#     a.nivel_eutrofizacion = fuz_predictions.iloc[i]['eutrofizacion']
#     predicts.append(a.obtener_etiqueta())

# plot_categorical_comparison(originals, predicts, x_label="PREDICCIÓN DIRECTA", y_label="INFERENCIA DIFUSA")

# plot_categorical_comparison(originals, fuzis, x_label="PREDICCIÓN DIFUZA", y_label="INFERENCIA DIFUSA")

# last_series = data_serie_filled.iloc[-12:]

# tsi_s = []
# for index, row in last_series.iterrows():
#     tsi = calculate_tsi_individual(np.nan, np.nan, row['Chl_a']*1000)
#     tsi_s.append(tsi['Level_Chl_a'])

# plot_categorical_comparison(tsi_s, predicts, x_label="PREDICCIÓN DIRECTA", y_label="TSI Chl-A")

# plot_categorical_comparison(tsi_s, fuzis, x_label="PREDICCIÓN DIFUZA", y_label="TSI Chl-A")