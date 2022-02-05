import enum
from ..models.Application import Application
from .. import db
from .User import User
from datetime import datetime

class RecommendationStatusEnum(str, enum.Enum):
    Recommended = "Recommended"
    Not_Recommended = "Not Recommended"

class Recommendations(db.Model):
    __tablename__ = 'la_t_Recommendations'
    RecommendationId = db.Column(db.Integer, primary_key=True)
    ApplicationId = db.Column(db.Integer, db.ForeignKey(Application.ApplicationId), nullable=False) 
    RecommendationStatus = db.Column(db.Enum(RecommendationStatusEnum,
                                     values_callable=lambda x: [str(e.value) for e in RecommendationStatusEnum]))
    DeclineReason = db.Column(db.VARCHAR(150),nullable=True)
    Date = db.Column(db.DateTime)
    Handler = db.Column(db.Integer, db.ForeignKey(User.UserId),nullable=False) 
    CreationDate = db.Column(db.DateTime,default=datetime.utcnow)
    UpdateDate = db.Column(db.DateTime,default=datetime.utcnow,onupdate=db.func.current_timestamp())

    
    def serialise(self):
        '''serialize model object into json object'''
        json_obj = {}
        for column in self.__table__.columns:
            json_obj[column.name] = str(getattr(self, column.name))
        return json_obj
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
