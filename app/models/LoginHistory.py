from .. import db
from .User import User

class LoginHistory(db.Model):
    __tablename__ = 'la_t_LoginHistory'
    LoginHistoryId = db.Column(db.Integer,primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey(User.UserId),nullable=False) 
    UserOnlineStatus = db.Column(db.SMALLINT)  
    LogLoginDate = db.Column(db.DateTime)  
    LogLogoutDate = db.Column(db.DateTime)
    
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
