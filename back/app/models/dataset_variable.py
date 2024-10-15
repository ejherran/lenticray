# app/models/dataset_variable.py

from sqlalchemy import Table, Column, String, ForeignKey
from app.db.base_class import Base

dataset_variable = Table(
    'dataset_variable',
    Base.metadata,
    Column('dataset_id', String, ForeignKey('datasets.id'), primary_key=True),
    Column('variable_id', String, ForeignKey('variables.id'), primary_key=True)
)