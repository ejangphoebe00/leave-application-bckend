from .. import db
import enum
from flask_bcrypt import Bcrypt
from datetime import datetime


class UserCatgoryEnum(str, enum.Enum):
    HR = "HR"
    Director = "Director"
    E_Director = "Executive Director"
    Other_Staff = "Other Staff"

class DirectorateEnum(str, enum.Enum):
    IT = "ICT and Data Managment"
    Development = "Development and Producation"
    Exploration = "Exploration"
    Technical_Support = "Technical Support And Service"
    PRCT = "PRCT(Petroleum, Refinery, Conversion and Tranmission and Storage)"
    ED = "Office of the Executive Director"
    Affairs = "Legal and Corporate Affairs"
    Administration = "Fianance And Adminsitration"
    Environment = "Environment, Health and Safety"

class User(db.Model):
    __tablename__ = 'la_t_User'
    UserId = db.Column(db.Integer,primary_key=True)
    FirstName = db.Column(db.NVARCHAR(255),nullable=False)
    MiddleName = db.Column(db.NVARCHAR(255),nullable=True)
    Surname = db.Column(db.NVARCHAR(255),nullable=False)
    LUID = db.Column(db.Integer)
    UserName = db.Column(db.NVARCHAR(255),nullable=False, unique=True)
    LoginID = db.Column(db.NVARCHAR(255),nullable=True)
    LoginIDAlias = db.Column(db.NVARCHAR(255), nullable=True)
    UserCategory = db.Column(db.Enum(UserCatgoryEnum,
                                     values_callable=lambda x: [str(e.value) for e in UserCatgoryEnum]),
                                     nullable=False)
    UserCompanyId = db.Column(db.Integer)
    UserPremsUserId = db.Column(db.Integer)
    Directorate = db.Column(db.Enum(DirectorateEnum,
                                     values_callable=lambda x: [str(e.value) for e in DirectorateEnum]),
                                     nullable=False)
    NextOfKinName = db.Column(db.NVARCHAR(255),nullable=False)
    StaffId = db.Column(db.Integer, unique=True)
    OrganisationName = db.Column(db.NVARCHAR(255),nullable=True)
    UserPassword = db.Column(db.NVARCHAR(255),nullable=True)
    UserEmailAddress = db.Column(db.NVARCHAR(255),nullable=False, unique=True)
    UserSecurityLevelId = db.Column(db.Integer)
    UserNogtrWebSecurityLevelId = db.Column(db.Integer)
    UserPremsWebSecurityLevelId = db.Column(db.Integer)
    UserIntranetSecurityLevelId = db.Column(db.Integer)
    UserNsdWebSecurityLevelId = db.Column(db.Integer)
    LoginErrorCount = db.Column(db.Integer)
    LoginStatusId = db.Column(db.Integer)
    LastSeen = db.Column(db.DateTime,nullable=True)
    DeactivateAccount = db.Column(db.SMALLINT,nullable=True)
    ActivationChangeComment = db.Column(db.NVARCHAR(255),nullable=True)
    ActivationChangeDate = db.Column(db.DateTime, nullable=True)
    CredentialsSent = db.Column(db.SMALLINT, nullable=True)
    UserOnlineStatus = db.Column(db.SMALLINT, nullable=True)
    Comments = db.Column(db.NVARCHAR(500),nullable=True)
    OrganisationUserName = db.Column(db.NVARCHAR(255),nullable=True, default='Petroleum Authority of Uganda')
    ProfilePicture = db.Column(db.NVARCHAR(225), nullable=True)
    DateCreated = db.Column(db.DateTime,default=datetime.utcnow)
    ModifiedOn = db.Column(db.DateTime,default=datetime.utcnow,onupdate=db.func.current_timestamp())
    ModifiedBy = db.Column(db.NVARCHAR(255),nullable=True)
    RecordChangeStamp = db.Column(db.NVARCHAR(100),nullable=True)
    DefaultChangeDate = db.Column(db.DateTime,default=datetime.utcnow, onupdate=db.func.current_timestamp())
    PasswordChangeDate = db.Column(db.DateTime,default=db.func.current_timestamp(),nullable=True)
    # Applications = db.relationship('Application', backref='la_t_User',lazy=True)
    
    def __repr__(self):
        return '<CraneUser {}>'.format(self.CraneUserName)
    
    def serialise(self):
        '''serialize model object into json object'''
        json_obj = {}
        for column in self.__table__.columns:
            json_obj[column.name] = str(getattr(self, column.name))
        return json_obj
    
    # can be called without an object for this class
    @staticmethod
    def hash_password(password):
        '''use bcrypt to hash passwords'''
        return Bcrypt().generate_password_hash(password).decode()

    def is_password_valid(self, password):
        '''Check the password against it's hash to validates the user's password
            (returns True if passwords match)
        '''
        return Bcrypt().check_password_hash(self.UserPassword, password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
