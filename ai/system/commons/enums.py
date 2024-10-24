import enum

class OperationMode(enum.Enum):
    TRAIN = "TRAIN"
    PREDICT = "PREDICT"

class EutrophicationLevel(enum.Enum):
    UNKNOWN = "UNKNOWN"
    OLIGOTROPHIC = "OLIGOTROPHIC"
    MESOTROPHIC = "MESOTROPHIC"
    EUTROPHIC = "EUTROPHIC"
    HYPEREUTROPHIC = "HYPEREUTROPHIC"

class TemporalSpace(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"