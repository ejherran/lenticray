import pydantic

from system.commons import enums

class Settings(pydantic.BaseModel):
    id: str
    base_path: str
    work_dir: str
    window_size: int


class TrainSettings(Settings):
    temporal_space: enums.TemporalSpace
    target_body: str

    @property
    def data_file(self):
        return f'{self.base_path}/{self.work_dir}/data.parquet'


class PredictSettings(Settings):
    output_tag: str
    amount: int

    @property
    def data_file(self):
        return f'{self.base_path}/{self.work_dir}/fuzzy.parquet'
    
    @property
    def model_file(self):
        return f'{self.base_path}/{self.work_dir}/model.keras'
    
    @property
    def output_file(self):
        return f'{self.base_path}/{self.work_dir}/{self.output_tag}.parquet'