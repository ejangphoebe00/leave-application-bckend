import enum
from .. import db
from .User import User
from datetime import datetime

class ApplicantLevelEnum(str, enum.Enum):
    Staff = "Staff"
    Senior_officer = "Senior Officer"
    Manager = "Manager"
    Director = "Director"

class LeaveTypeEnum(str, enum.Enum):
    Annual = "Annual Leave"
    Study = "Study Leave"
    Sick = "Sick Leave"
    Maternity = "Maternity Leave"
    Paternity = "Paternity Leave"
    Compassionate = "Compassionate Leave"

class ApprovalStatusEnum(str, enum.Enum):
    Approved = "Approved"
    Not_Approved = "Not Approved"

class Application(db.Model):
    __tablename__ = 'la_t_Applications'
    ApplicationId = db.Column(db.Integer,primary_key=True)
    Designation = db.Column(db.VARCHAR(100),nullable=False) 
    ApplicantLevel = db.Column(db.Enum(ApplicantLevelEnum,
                                     values_callable=lambda x: [str(e.value) for e in ApplicantLevelEnum]),
                                     nullable=False) 
    ApplicantId = db.Column(db.Integer, db.ForeignKey(User.UserId),nullable=False) 
    TypeOfLeave = db.Column(db.Enum(LeaveTypeEnum,
                                     values_callable=lambda x: [str(e.value) for e in LeaveTypeEnum]),
                                     nullable=False) 
    NumberOfDaysNeeded = db.Column(db.Integer)
    ReturnDate = db.Column(db.Date)
    LeaveCommencement = db.Column(db.Date)
    ApplicationDate = db.Column(db.DateTime)
    LeaveBalanceBroughtForward = db.Column(db.Integer)
    LeaveDueInYear = db.Column(db.Integer)
    LessLeaveTaken = db.Column(db.Integer)
    BalanceCarriedForward = db.Column(db.Integer)
    ComputedBy = db.Column(db.Integer, db.ForeignKey(User.UserId)) 
    VerifiedBy = db.Column(db.Integer, db.ForeignKey(User.UserId)) 
    ApprovalStatus = db.Column(db.Enum(ApprovalStatusEnum,
                                     values_callable=lambda x: [str(e.value) for e in ApprovalStatusEnum]))
    DeclineReason = db.Column(db.NVARCHAR(255),nullable=True)
    ApprovedOrDeclinedBy = db.Column(db.Integer, db.ForeignKey(User.UserId)) 
    CreationDate = db.Column(db.DateTime,default=datetime.utcnow)
    UpdateDate = db.Column(db.DateTime,default=datetime.utcnow,onupdate=db.func.current_timestamp())

    # since there's only one foreign key in these respective tables....
    AddressDetails = db.relationship('Address', backref='la_t_Applications', lazy=True)
    Recommendations = db.relationship('Recommendations', backref='la_t_Applications', lazy=True)

    # since there are many foregn keys to the user table, advisable to declare relationships like this
    Computed = db.relationship("User", foreign_keys=[ComputedBy])
    Verified = db.relationship("User", foreign_keys=[VerifiedBy])
    ApprovedOrDeclined = db.relationship("User", foreign_keys=[ApprovedOrDeclinedBy])
    Applicant = db.relationship("User", foreign_keys=[ApplicantId])


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
