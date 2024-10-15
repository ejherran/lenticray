from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate
import uuid

class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def get_multi_by_study(
        self, db: Session, *, study_id: str, skip: int = 0, limit: int = 100
    ) -> List[Prediction]:
        return (
            db.query(Prediction)
            .filter(Prediction.study_id == study_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_study(
        self, db: Session, *, obj_in: PredictionCreate, study_id: str
    ) -> Prediction:
        db_obj = Prediction(
            id=str(uuid.uuid4()),
            study_id=study_id,
            name=obj_in.name,
            window_size=obj_in.window_size,
            amount=obj_in.amount,
            status="PENDING",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

prediction = CRUDPrediction(Prediction)
