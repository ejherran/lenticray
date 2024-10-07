import pandas as pd

from loguru import logger

from ai.commons import enums, dto
from ai.tools import spacer
from ai.imputation import dual
from ai.prediction import lstm
from ai.fuzzy import engine

_BASE_COLUMNS = [
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


def execute(
    *,
    config: dto.TrainSettings   
) -> None:
    logger.info("RUNNING TRAIN...")
    
    df = get_dataframe(
        data_file=config.data_file,
        target_body=config.target_body
    )

    df = fix_temporal_space(
        df=df,
        config=config
    )

    features = get_features(df=df)

    df = set_data_serie(
        config=config,
        df=df,
        features=features
    )

    df = impute_data(df=df, features=features)

    fuz_df, fuz_features = run_fuzzy(df=df, config=config)

    train_model(
        fuz_data=fuz_df,
        fuz_features=fuz_features,
        config=config
    )

    logger.info("TRAIN FINISHED")
    
    
def get_dataframe(
    *,
    data_file: str,
    target_body: str
) -> pd.DataFrame:
    logger.info("1. Getting dataframe...")

    df =  pd.read_parquet(data_file)

    target_data = df[df['Water Body'] == target_body]
    target_data.reset_index(drop=True, inplace=True)

    return target_data


def fix_temporal_space(
    *,
    df: pd.DataFrame,
    config: dto.TrainSettings,
) -> pd.DataFrame:
    logger.info(f"2. Fix time space to {config.temporal_space.value}...")

    df = spacer.process_data_in_temporal_space(df, config.temporal_space)

    if config.temporal_space == enums.TemporalSpace.MONTHLY:
        df = df.sort_values(by=['Year', 'Month'])

    elif  config.temporal_space == enums.TemporalSpace.WEEKLY:
        df = df.sort_values(by=['Year', 'Week'])

    elif config.temporal_space == enums.TemporalSpace.DAILY:
        df = df.sort_values(by=['Year', 'Month', 'Day'])
    
    return df


def get_features(
    *,
    df: pd.DataFrame,
) -> list[str]:
    logger.info("3. Getting features...")

    non_null_columns = df.columns[df.notna().any()].tolist()
    features = [col for col in _BASE_COLUMNS if col in non_null_columns]

    return features


def set_data_serie(
    *,
    config: dto.TrainSettings,
    df: pd.DataFrame,
    features: list[str]
) -> pd.DataFrame:
    logger.info("4. Setting data serie...")

    if config.temporal_space == enums.TemporalSpace.MONTHLY:
        data_serie = df[features + ['Year', 'Month']]

    elif  config.temporal_space == enums.TemporalSpace.WEEKLY:
        data_serie = df[features + ['Year', 'Week']]

    elif config.temporal_space == enums.TemporalSpace.DAILY:
        data_serie = df[features + ['Year', 'Month', 'Day']]
    
    return data_serie


def impute_data(
    *,
    df,
    features
) -> pd.DataFrame:
    logger.info("5. Imputing data with GRUD and LSTM...")
    
    data_serie_filled = dual.dual_imputation(df, features)

    return data_serie_filled


def run_fuzzy(
    *,
    df: pd.DataFrame,
    config: dto.TrainSettings
) -> tuple[pd.DataFrame, list[str]]:
    logger.info("6. Running fuzzy engine...")

    logger.info("6. Ejecución del motor de inferencia difusa...")
    fuz_data_serie, _, _ = engine.ejecutar_motor(df)

    fuz_vars = ['eutrofizacion', 'quimicas', 'fisicas', 'adicionales']
    fuz_data = {
        'eutrofizacion': [],
        'quimicas': [],
        'fisicas': [],
        'adicionales': []
    }

    fuz_tags = {
        'eutrofizacion': [],
        'quimicas': [],
        'fisicas': [],
        'adicionales': []
    }

    for i in fuz_data_serie:
        for c in fuz_vars:
            fuz_data[c].append(i[c]['valor'])
            fuz_tags[c].append(i[c]['etiqueta'])

    fuz_data = pd.DataFrame(fuz_data)
    fuz_tags = pd.DataFrame(fuz_tags)
    fuz_data.info()

    fuz_data.to_parquet(f'{config.base_path}/{config.work_dir}/fuzzy.parquet')
    fuz_tags.to_parquet(f'{config.base_path}/{config.work_dir}/fuzzy_tags.parquet')

    return fuz_data, fuz_vars


def train_model(
    *,
    fuz_data: pd.DataFrame,
    fuz_features: list[str],
    config: dto.TrainSettings
) -> None:
    logger.info("7. Training Predictive Model...")

    lstm.lstm_triain(
        fuzz_data=fuz_data,
        window_size=config.window_size,
        features=fuz_features,
        work_dir=f'{config.base_path}/{config.work_dir}'
    )

    return None