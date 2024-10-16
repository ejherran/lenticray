# app/crud/dataset.py

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.models.variable import Variable

class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    def create_with_project(
        self, db: Session, *, obj_in: DatasetCreate, project_id: str
    ) -> Dataset:
        db_obj = Dataset(
            name=obj_in.name,
            project_id=project_id,
        )
        db_obj.variables = db.query(Variable).filter(Variable.id.in_(obj_in.variable_ids)).all()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_project(
        self, db: Session, *, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Dataset]:
        return (
            db.query(self.model)
            .filter(Dataset.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, db: Session, *, db_obj: Dataset, obj_in: Dict[str, Any]
    ) -> Dataset:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        # Filtrar solo el campo 'name'
        update_data = {'name': update_data['name']}
        return super().update(db=db, db_obj=db_obj, obj_in=update_data)

dataset = CRUDDataset(Dataset)
