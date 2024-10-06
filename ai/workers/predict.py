import pandas as pd
import numpy as np

from loguru import logger

from ai.commons import enums, dto
from ai.prediction import lstm
from ai.fuzzy.componentes import eutrophication, chemical, physical, aditional

def execute(
    *,
    config: dto.PredictSettings
)-> None:
    logger.info("RUNNING PREDICT...")

    fuz_data = pd.read_parquet(config.data_file)
    features = ['eutrofizacion', 'quimicas', 'fisicas', 'adicionales']
    
    predictions = lstm.only_prediction(
        fuzz_data=fuz_data,
        model_file=config.model_file,
        window_size=config.window_size,
        features=features,
        num_predictions=config.amount,
    )

    fuz_tags = {
        'eutrofizacion': [],
        'eutrofizacion_inferida': [],
        'quimicas': [],
        'fisicas': [],
        'adicionales': []
    }

    for i in range(predictions.shape[0]):
        a = eutrophication.NivelEutrofizacion(
            predictions.iloc[i]['quimicas'],
            predictions.iloc[i]['fisicas'],
            predictions.iloc[i]['adicionales']
        )
        a.calcular_inferencia()
        fuz_tags['eutrofizacion_inferida'].append(a.obtener_etiqueta())

        a.nivel_eutrofizacion = predictions.iloc[i]['eutrofizacion']
        fuz_tags['eutrofizacion'].append(a.obtener_etiqueta())

        a = chemical.CondicionesQuimicas(0.1, 0.1)
        a.condiciones_quimicas = predictions.iloc[i]['quimicas']
        fuz_tags['quimicas'].append(a.obtener_etiqueta())

        a = physical.CondicionesFisicas(0.1, 0.1)
        a.condiciones = predictions.iloc[i]['fisicas']
        fuz_tags['fisicas'].append(a.obtener_etiqueta())

        a = aditional.CondicionesAdicionales(**{'TEMP': 0.1, 'PH': 0.1})
        a.condiciones = predictions.iloc[i]['adicionales']
        fuz_tags['adicionales'].append(a.obtener_etiqueta())

    fuz_tags = pd.DataFrame(fuz_tags)
    predictions.to_parquet(config.output_file)
    fuz_tags.to_parquet(config.output_file.replace('.parquet', '_tags.parquet'))

    
    logger.info("FINISHED PREDICT")