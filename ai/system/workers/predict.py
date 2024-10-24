import pandas as pd
import numpy as np

from loguru import logger

from system.commons import enums, dto
from system.prediction import lstm
from system.fuzzy.componentes import eutrophication, chemical, physical, aditional

def execute(
    *,
    config: dto.PredictSettings
)-> None:
    logger.info("RUNNING PREDICT...")

    fuz_data = pd.read_parquet(config.data_file)
    features = fuz_data.columns.tolist()
    
    predictions = lstm.only_prediction(
        fuzz_data=fuz_data,
        model_file=config.model_file,
        window_size=config.window_size,
        features=features,
        num_predictions=config.amount,
    )

    fuz_tags = {
        feature: [] for feature in features
    }
    fuz_tags['inferred_eutrophication_level_tag'] = []

    for i in range(predictions.shape[0]):

        chemical_conditions = predictions.iloc[i]['chemical_conditions'] if 'chemical_conditions' in features else np.nan
        physical_conditions = predictions.iloc[i]['physical_conditions'] if 'physical_conditions' in features else np.nan
        additional_conditions = predictions.iloc[i]['additional_conditions'] if 'additional_conditions' in features else np.nan

        a = eutrophication.EutrophicationLevel(
            chemical_conditions=chemical_conditions,
            physical_conditions=physical_conditions,
            additional_conditions=additional_conditions
        )
        a.calculate_inference()
        fuz_tags['inferred_eutrophication_level_tag'].append(a.get_label())

        a.eutrophication_level = predictions.iloc[i]['eutrophication_level']
        fuz_tags['eutrophication_level'].append(a.get_label())

        if 'chemical_conditions' in features:
            a = chemical.ChemicalConditions(0.1, 0.1)
            a.chemical_conditions = predictions.iloc[i]['chemical_conditions']
            fuz_tags['chemical_conditions'].append(a.get_label())

        if 'physical_conditions' in features:
            a = physical.PhysicalConditions(0.1, 0.1)
            a.physical_conditions = predictions.iloc[i]['physical_conditions']
            fuz_tags['physical_conditions'].append(a.get_label())

        if 'additional_conditions' in features:
            a = aditional.AdditionalConditions(**{'TEMP': 0.1, 'PH': 0.1})
            a.additional_conditions = predictions.iloc[i]['additional_conditions']
            fuz_tags['additional_conditions'].append(a.get_label())

    fuz_tags = pd.DataFrame(fuz_tags)
    predictions.to_parquet(config.output_file)
    fuz_tags.to_parquet(config.output_file.replace('.parquet', '_tags.parquet'))

    
    logger.info("FINISHED PREDICT")