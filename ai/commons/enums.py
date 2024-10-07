import enum

class OperationMode(enum.Enum):
    TRAIN = "TRAIN"
    PREDICT = "PREDICT"

class EutrophicationLevel(enum.Enum):
    UNKNOWN = "DESCONOCIDO"
    OLIGOTROPHIC = "OLIGOTRÓFICO"
    MESOTROPHIC = "MESOTRÓFICO"
    EUTROPHIC = "EUTRÓFICO"
    HYPEREUTROPHIC = "HIPEREUTRÓFICO"

class TemporalSpace(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"