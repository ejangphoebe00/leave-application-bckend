from ..models.Application import Application
from .. import db

class Address(db.Model):
    __tablename__ = 'la_t_Address'
    AddressId = db.Column(db.Integer,primary_key=True)
    ApplicationId = db.Column(db.Integer, db.ForeignKey(Application.ApplicationId),nullable=False) 
    AddressDetail = db.Column(db.NVARCHAR(150),nullable=False)
    Telephone = db.Column(db.NVARCHAR(50),nullable=False)
    NextOfKinContact = db.Column(db.NVARCHAR(50),nullable=False)
    
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
