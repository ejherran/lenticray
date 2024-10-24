import pandas as pd
from system.imputation import grud, lstm



def dual_imputation(data_serie, numeric_columns):
    data_serie_filled = data_serie.copy()

    grud_data_imputed = grud.grud_imputation(data_serie)
    grud_data_imputed = grud_data_imputed.reset_index(drop=True)

    lstm_data_imputed = lstm.lstm_imputation(data_serie, numeric_columns)

    for column in data_serie.columns:
        for index in data_serie.index:
            if pd.isnull(data_serie.loc[index, column]):
                imputed_value = grud_data_imputed.loc[index, column]
                crazy_prediction_value = lstm_data_imputed.loc[index, column]
                data_serie_filled.loc[index, column] = (imputed_value * 0.7) + (crazy_prediction_value * 0.3)

    return data_serie_filled