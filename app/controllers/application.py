from email.mime import application
from flask import Blueprint, request, make_response, jsonify, current_app

from app.models.Address import Address
from app.models.Recommendations import Recommendations
from app.models.User import User
from ..models.Application import Application
import traceback
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from .. import db
from datetime import datetime

application_bp = Blueprint('application_bp', __name__)

@application_bp.route('/apiv1/apply_for_leave',methods=['POST'])
@jwt_required()
def apply_for_leave():
    data = request.get_json(force=True)
    try:
        application = Application(
            ApplicantLevel = data['ApplicantLevel'],
            Designation = data['Designation'],
            ApplicantId = data['ApplicantId'],
            TypeOfLeave = data['TypeOfLeave'],
            NumberOfDaysNeeded = data['NumberOfDaysNeeded'],
            ReturnDate = data['ReturnDate'], 
            LeaveCommencement = data['LeaveCommencement'],
            ApplicationDate = data['ApplicationDate'] 
        )
        db.session.add(application)
        db.session.flush()

        if hasattr(data['AddressDetail'],'__iter__'):
            for i in range(len(data['AddressDetail'])):
                address = Address(
                    ApplicationId = application.ApplicationId,
                    AddressDetail = data['AddressDetail'][i],
                    Telephone = data['Telephone'][i],
                    NextOfKinContact = data['NextOfKinContact'][i],
                )
                db.session.add(address)
                db.session.flush()
        else:
            address = Address(
                ApplicationId = application.ApplicationId,
                AddressDetail = data['AddressDetail'],
                Telephone = data['Telephone'],
                NextOfKinContact = data['NextOfKinContact'],
            )
            db.session.add(address)
            db.session.flush()
        db.session.commit()
        resp = jsonify({'message': 'Application created successfully'})
        return make_response(resp, 201)
    except:
        db.session.rollback()
        return make_response(str(traceback.format_exc()),500)


@application_bp.route('/apiv1/update_leave_application/<int:ApplicationId>',methods=['PUT'])
@jwt_required()
def update_leave_application(ApplicationId):
    data = request.get_json(force=True)
    try:
        application = Application.query.get(ApplicationId)
        application.ApplicantLevel = data['ApplicantLevel']
        application.Designation = data['Designation']
        application.ApplicantId = data['ApplicantId']
        application.TypeOfLeave = data['TypeOfLeave']
        application.NumberOfDaysNeeded = data['NumberOfDaysNeeded']
        application.ReturnDate = data['ReturnDate']
        application.LeaveCommencement = data['LeaveCommencement']
        application.ApplicationDate = data['ApplicationDate']

        if hasattr(data['AddressDetail'],'__iter__'):
            for i in range(len(data['AddressDetail'])):
                address = Address.query.filter_by(ApplicationId=ApplicationId, AddressDetail=data['AddressDetail'][i]).first()
                address.AddressDetail = data['AddressDetail'][i]
                address.Telephone = data['Telephone'][i]
                address.NextOfKinContact = data['NextOfKinContact'][i]
        else:
            address = Address.query.filter_by(ApplicationId=ApplicationId).first()
            address.AddressDetail = data['AddressDetail']
            address.Telephone = data['Telephone']
            address.NextOfKinContact = data['NextOfKinContact']
        db.session.commit()
        resp = jsonify({'message': 'Application created successfully'})
        return make_response(resp, 201)
    except:
        db.session.rollback()
        return make_response(str(traceback.format_exc()),500)


@application_bp.route('/apiv1/get_user_applications/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_applications(user_id):
    try:
        applications = [z.serialise() for z in Application.query.filter_by(ApplicantId = user_id)]

        resp = jsonify(applications)
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)


@application_bp.route('/apiv1/get_single_application/<int:ApplicationId>', methods=['GET'])
@jwt_required()
def get_single_application(ApplicationId):
    try:
        applications = Application.query.get(ApplicationId)

        resp = jsonify(applications)
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)


@application_bp.route('/apiv1/get_all_applications', methods=['GET'])
@jwt_required()
def get_all_applications():
    try:
        num_of_items = current_app.config['NUM_OF_ITEMS_PER_PAGE']
        page = request.args.get('page', 1, type=int)
        applications = [z.serialise() for z in Application.query.paginate(page, num_of_items, False).items]

        resp = jsonify(applications)
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)

# by hr
@application_bp.route('/apiv1/compute_application/<int:ApplicationId>', methods=['PUT'])
@jwt_required()
def compute_application(ApplicationId):
    try:
        data = request.get_json(force=True)
        user = User.query.filter_by(email=get_jwt_identity()).first()
        application = Application.query.get(ApplicationId)
        application.LeaveBalanceBroughtForward = data['LeaveBalanceBroughtForward']
        application.LeaveDueInYear = data['LeaveDueInYear']
        application.LessLeaveTaken = data['LessLeaveTaken']
        application.BalanceCarriedForward = data['BalanceCarriedForward']
        application.ComputedBy = user.UserId
        application.VerifiedBy = user.UserId
        application.update()

        resp = jsonify({'message': 'Computation added'})
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)


# edit
@application_bp.route('/apiv1/approve_application/<int:ApplicationId>', methods=['PUT'])
@jwt_required()
def approve_application(ApplicationId):
    try:
        data = request.get_json(force=True)
        user = User.query.filter_by(email=get_jwt_identity()).first()
        application = Application.query.get(ApplicationId)
        application.ApprovalStatus = data['ApprovalStatus']
        application.DeclineReason = data['DeclineReason']
        application.ApprovedOrDeclinedBy = user.UserId
        application.update()

        resp = jsonify({'message': 'Approval status captured'})
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)


@application_bp.route('/apiv1/add_recommendation/<int:ApplicationId>', methods=['POST'])
@jwt_required()
def add_recommendation(ApplicationId):
    try:
        data = request.get_json(force=True)
        user = User.query.filter_by(email=get_jwt_identity()).first()
        recommendation = Recommendations(
            ApplicationId = ApplicationId,
            RecommendationStatus = data['RecommendationStatus'],
            DeclineReason = data['DeclineReason'],
            Date = datetime.utcnow,
            Handler = user.UserId
        )
        recommendation.save()

        resp = jsonify({'message': 'Recommendation added'})
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)

