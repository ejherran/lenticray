from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.study import Study
from app.schemas.study import StudyCreate, StudyUpdate
import uuid

class CRUDStudy(CRUDBase[Study, StudyCreate, StudyUpdate]):
    def get_multi_by_project(
        self, db: Session, *, project_id: str, skip: int = 0, limit: int = 100
    ) -> List[Study]:
        return (
            db.query(Study)
            .filter(Study.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_project(
        self, db: Session, *, obj_in: StudyCreate, project_id: str
    ) -> Study:
        db_obj = Study(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            project_id=project_id,
            dataset_id=obj_in.dataset_id,
            time_space=obj_in.time_space,
            window_size=obj_in.window_size,
            status="NEW",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

study = CRUDStudy(Study)