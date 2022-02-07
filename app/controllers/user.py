from flask import Blueprint, request, make_response, jsonify
from ..models.User import User, UserCatgoryEnum
from ..models.Token import RevokedTokenModel
from ..models.LoginHistory import LoginHistory
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from datetime import datetime, timedelta
from .helper_functions import send_security_alert_email, upload_file, reset_token, send_reset_email
import traceback
from ..models.PasswordReset import PasswordReset


auth_bp = Blueprint('auth_bp', __name__)

# user login
@auth_bp.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        email = data['UserEmailAddress']
        user = User.query.filter(User.UserEmailAddress==email,User.DeactivateAccount==0).first()###
        password = data['UserPassword']
        
        access_token = create_access_token(identity = data['UserEmailAddress'])
        refresh_token = create_refresh_token(identity = data['UserEmailAddress'])
        if not user:
            return make_response(jsonify({"message":"Account doesn't exist"}),400)
        if not user.is_password_valid(password):
            # increment counter
            user.LoginErrorCount += 1
            user.update()
            if user.LoginErrorCount >= 3:
                # send email to account owner
                print('so many attempts')
                send_security_alert_email(email)
            return make_response(jsonify({"message":"Invalid credentials"}),400)
        # reset counter
        user.LoginErrorCount = 0
        user.UserOnlineStatus = 1
        user.update()

        # update login history
        login_history = LoginHistory(
            UserId = user.UserId,
            LoginStatusId = 0,   
            UserOnlineStatus = 1,
            LogLoginDate = datetime.now()
        )
        login_history.save()
        # if user.UserCategory == UserCatgoryEnum.App_Admin:
        #     user_role = "Application Admin"
        # elif user.UserCategory == UserCatgoryEnum.Data_Admin:
        #     user_role = "Data Admin"
        # else:
        #     user_role = "Staff"
        resp = jsonify({"UserId":user.UserId,"user_role":user.UserCategory,'access_token':access_token,
                        'refresh_token':refresh_token,'message':'Login Successful'
                    })
        return make_response(resp,200)
    except:
        return make_response(str(traceback.format_exc()),500)


# User registration
@auth_bp.route('/user/registration', methods=['POST'])
def register_user():
    """Create a user."""
    current_user_email = get_jwt()
    user = User.query.filter_by(UserEmailAddress=current_user_email['sub']).first()
    try:
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = request.form
        existing_user = User.query.filter(User.UserEmailAddress == data['UserEmailAddress']).first()
        if existing_user:
            return make_response(jsonify({'message': 'User already exists!'}), 400)

        staff = User.query.filter(User.UserStaffId == data['UserStaffId']).first()
        if staff and staff.UserStaffId != None:
            return make_response(jsonify({'message': 'StaffID already exists!'}), 400)

        if User.query.filter(User.UserName==data['UserName']).first():
            return make_response(jsonify({'message': 'Username already exists!'}), 400)

        # create new user
        new_user = User(
                        FirstName = data['FirstName'],
                        MiddleName = data['MiddleName'],
                        Surname = data['Surname'],
                        LUID = data['LUID'],
                        UserName = data['UserName'],
                        LoginID = data['LoginID'],
                        LoginIDAlias = data['LoginIDAlias'],
                        UserCategory = data['UserCategory'],
                        UserCompanyId = data['UserCompanyId'],
                        UserPremsUserId = data['UserPremsUserId'],
                        UserStaffId = data['UserStaffId'],
                        OrganisationName = data['OrganisationName'],
                        CredentialsSent = 1,
                        UserEmailAddress = data['UserEmailAddress'],
                        UserSecurityLevelId = data['UserSecurityLevelId'],
                        UserNogtrWebSecurityLevelId = data['UserNogtrWebSecurityLevelId'],
                        UserPremsWebSecurityLevelId = data['UserPremsWebSecurityLevelId'],
                        UserIntranetSecurityLevelId = data['UserIntranetSecurityLevelId'],
                        UserNsdWebSecurityLevelId = data['UserNsdWebSecurityLevelId'],
                        Comments = data['Comments'],
                        OrganisationUserName = data['OrganisationUserName'],
                        NextOfKinName = data['NextOfKinName'],
                        Directorate = data['Directorate'],
                        CreatedById = user.UserId,
                        DeactivateAccount = 0,
                        LoginErrorCount = 0,
                        UserPassword = User.hash_password(data['UserPassword']),
                    )
        new_user.save()

        resp = jsonify({'message': 'Account created successfully'})
        return make_response(resp, 201)
    except:
        return make_response(str(traceback.format_exc()),500)


@auth_bp.route('/user/get_user/<int:UserId>', methods=['GET'])
@jwt_required()
def get_user(UserId):
    try:
        user = User.query.get(UserId)
        return make_response(jsonify(user.serialise()),200)
    except:
        return make_response(str(traceback.format_exc()),500)


# # deactivate account
# @auth_bp.route('/user/deactivate_account/<int:UserId>', methods=['PUT'])
# @jwt_required()
# def deactivate_account(UserId):
#     try:
#         user = User.query.get(UserId)
#         user.DeactivateAccount = 1
#         user.update()
#         return make_response(jsonify({'message':'Account successfully Deactivated'}),200)
#     except:
#         return make_response(str(traceback.format_exc()),500)
      

# # reactivate account
# @auth_bp.route('/user/reactivate_account/<int:UserId>', methods=['PUT'])
# @jwt_required()
# def reactivate_account(UserId):
#     try:
#         user = User.query.get(UserId)
#         user.DeactivateAccount = 0
#         user.update()
#         return make_response(jsonify({'message':'Account successfully Reactivated'}),200)
#     except:
#         return make_response(str(traceback.format_exc()),500)


# Edit profile
@auth_bp.route('/user/edit_profile/<int:UserId>', methods=['PUT'])
@jwt_required()
def edit_profile(UserId):
    """Edit user details."""
    try:
        if request.is_json:
            data = request.get_json(force=True)
        else:
            data = request.form

        # user whose records are going to be updated
        user = User.query.get(UserId)
        # logged in user details
        current_user_email = get_jwt()
        loggedin_user = User.query.filter_by(UserEmailAddress=current_user_email['sub']).first()
        
        # check for redundancy
        staff = User.query.filter(User.UserStaffId == data['UserStaffId']).first()
        if staff and staff.UserStaffId != None:
            if UserId != staff.UserId:
                return make_response(jsonify({'message': 'StaffID already exists!'}), 400)

        staff_name = User.query.filter(User.UserName==data['UserName']).first()
        if staff_name:
            if UserId != staff_name.UserId:
                return make_response(jsonify({'message': 'Username already exists!'}), 400)

        user.FirstName = data['FirstName']
        user.MiddleName = data['MiddleName']
        user.Surname = data['Surname']
        user.LUID = data['LUID']
        user.UserName = data['UserName']
        user.LoginID = data['LoginID']
        user.LoginIDAlias = data['LoginIDAlias']
        user.UserCategory = data['UserCategory']
        user.UserCompanyId = data['UserCompanyId']
        user.UserPremsUserId = data['UserPremsUserId']
        user.UserStaffId = data['UserStaffId']
        user.OrganisationName = data['OrganisationName']
        user.UserEmailAddress = data['UserEmailAddress']
        user.UserSecurityLevelId = data['UserSecurityLevelId']
        user.UserNogtrWebSecurityLevelId = data['UserNogtrWebSecurityLevelId']
        user.UserPremsWebSecurityLevelId = data['UserPremsWebSecurityLevelId']
        user.UserIntranetSecurityLevelId = data['UserIntranetSecurityLevelId']
        user.UserNsdWebSecurityLevelId = data['UserNsdWebSecurityLevelId']
        user.Comments = data['Comments']
        user.OrganisationUserName = data['OrganisationUserName']
        user.NextOfKinName = data['NextOfKinName']
        user.Directorate = data['Directorate']
        user.ActivationChangeComment = data['ActivationChangeComment']
        user.ActivationChangeDate = datetime.now()        
        user.ModifiedBy = loggedin_user.UserId
        if user.UserPassword != data.get('UserPassword'):
            user.UserPassword = User.hash_password(data.get('UserPassword')) if data.get('UserPassword') else None
            user.PasswordChangeDate = datetime.now() if data.get('UserPassword') else user.PasswordChangeDate
        user.update()

        resp = jsonify({'message': 'Details updated successfully'})
        return make_response(resp, 200)
    except:
        return make_response(str(traceback.format_exc()),500)


# user logout
@auth_bp.route('/user/logout/<int:UserId>', methods=['DELETE'])
@jwt_required()
def logout(UserId):
    jti = get_jwt()['jti']
    user = User.query.get(UserId)
    try:
        revoked_token = RevokedTokenModel(jti = jti)
        revoked_token.save()
        # update user object
        user.LastSeen = datetime.now()
        user.UserOnlineStatus = 0
        user.update()
        # update login history (update last inserted)
        login_history = LoginHistory.query.filter(LoginHistory.HistLogUserId==UserId)[-1]
        login_history.LogLogoutDate = datetime.now()
        login_history.update()
        return make_response(jsonify({'message': 'Logout successful'}),200)
    except:
        return make_response(str(traceback.format_exc()),500)


@auth_bp.route('/user/token-refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity = current_user)
    return make_response(jsonify({'access_token': access_token}),200)


@auth_bp.route('/user/upload_profile_picture/<int:UserId>', methods=['POST'])
@jwt_required()
def upload_profile_picture(UserId):
    try:
        data = request.files
        user = User.query.get(UserId)
        profileImage = upload_file(data['ProfilePicture'])
        user.ProfilePicture = profileImage
        user.update()
        return make_response(jsonify({'message': "Profile picture successfully uploaded"}),200)
    except:
        return make_response(str(traceback.format_exc()),500)


@auth_bp.route('/user/get_profileImage/<int:UserId>', methods=['GET'])
@jwt_required()
def get_profileImage(UserId):
    try:
        user = User.query.get(UserId) 
        return make_response(jsonify({'ProfilePicture': user.ProfilePicture}),200)
    except:
        return make_response(str(traceback.format_exc()),500)


# forgot password
# url is UI link for a password reset form
@auth_bp.route('/user/forgot_password_email_request/<string:url>',methods=['POST'])
def recover_password_email(url):
    '''email request for password recovery'''
    if request.is_json:
        data = request.get_json(force=True)
    else:
        data = request.form
    token = str(reset_token())
    user = User.query.filter_by(UserEmailAddress=data['UserEmailAddress']).first()
    if not user:
        return make_response(jsonify({'message': 'The email you supplied is not registered with us, please check your email and try again.'}),404)
    
    # unused token
    existing_record_inactive = PasswordReset.query.filter_by(UserId=user.UserId, HasActivated=False).first()
    if existing_record_inactive:
        creation_date = existing_record_inactive.CreationDate
        today = datetime.utcnow()
        delta = today - creation_date
        if delta.days > 1:
            existing_record_inactive.HasActivated = True
            existing_record_inactive.save()
            return make_response(jsonify({'message': 'Expired token, please restart the password reset process.'}))
    
    existing_record_active = PasswordReset.query.filter_by(UserId=user.UserId, HasActivated=True).first()
    if existing_record_active:
        send_reset_email(data['UserEmailAddress'],str(url))
        existing_record_active.ResetKey = token
        existing_record_active.HasActivated = False
        existing_record_active.update()
    else:
        send_reset_email(data['UserEmailAddress'],str(url))
        reset_password = PasswordReset(
            UserId = user.UserId,
            ResetKey = token,
        )
        reset_password.save()
    
    return make_response(jsonify({'message': 'An email has been sent with instructions to reset your password.'}),200)

# save  new password
@auth_bp.route('/user/store_updated_password/<int:UserId>', methods=['POST'])
def store_reset_password(UserId):
    '''update password'''
    data = request.get_json(force=True)

    user = User.query.get(UserId)
    user.UserPassword = User.hash_password(data['Password']),
    user.save()

    existing_record = PasswordReset.query.filter_by(UserId=UserId).first()
    existing_record.HasActivated = True
    existing_record.save()
    
    return make_response(jsonify({'message': 'Your password was successfully updated.'}),200)
