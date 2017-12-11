# project/server/auth/views.py


from flask import Blueprint, request, make_response, jsonify, session
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User, BlacklistToken

import pandas as pd
import wikidataintegrator as wdi

auth_blueprint = Blueprint('auth', __name__)


assay_data = \
    pd.read_csv('/Users/sebastianburgstaller/Documents/jupyter-notebooks/calibr_data/reframe_short_20170822.csv')
gvk_dt = pd.read_csv('/Users/sebastianburgstaller/Documents/jupyter-notebooks/calibr_data/gvk_data_to_release.csv')


ikey_wd_map = wdi.wdi_helpers.id_mapper('P235')
wd_ikey_map = dict(zip(ikey_wd_map.values(), ikey_wd_map.keys()))

print('wd ikey map length:', len(wd_ikey_map))


def get_assay_data(qid):
    tmp_dt = assay_data.loc[assay_data['wikidata'] == qid, :]

    ad = list()

    for c, x in tmp_dt.iterrows():
        tmp_obj = dict()

        # for k in x.keys():
        #     tmp_obj.update({k: x[k]})

        # only return the data really necessary for being rendered
        datamode = x['datamode']

        if datamode not in ['DECREASING', 'INCREASING', 'SUPER_ACTIVE']:
            continue
        elif datamode == 'DECREASING':
            tmp_obj.update({'activity_type': 'IC50'})
        elif datamode == 'INCREASING':
            tmp_obj.update({'activity_type': 'EC50'})
        elif datamode == 'SUPER_ACTIVE':
            tmp_obj.update({'activity_type': 'SUPER ACTIVE'})

        tmp_obj.update({'ac50': round(x['ac50'], 10)})
        tmp_obj.update({'assay_title': x['assay_title']})
        tmp_obj.update({'smiles': x['smiles']})
        tmp_obj.update({'PubChem CID': str(x['PubChem CID'])})
        tmp_obj.update({'wikidata': x['wikidata']})
        tmp_obj.update({'calibr_id': x['calibr_id']})
        tmp_obj.update({'inchi_key': x['inchi_key']})
        tmp_obj.update({'ref': 'Calibr'})


        ad.append(tmp_obj)

    return ad


def get_gvk_data(qid):
    ikey = wd_ikey_map[qid]
    print(ikey)

    tmp_dt = gvk_dt.loc[gvk_dt['ikey'] == ikey, :]

    ad = list()

    for c, x in tmp_dt.iterrows():
        tmp_obj = dict()

        tmp_obj.update({'drug_name': x['drug_name']})
        tmp_obj.update({'phase': x['phase'].split('; ')})
        tmp_obj.update({'drug_roa': x['drug_roa'].split('; ')})
        tmp_obj.update({'category': x['category'].split('; ')})
        tmp_obj.update({'mechanism': x['mechanism'].split('; ')})
        tmp_obj.update({'synonyms': x['synonyms'].split('; ')})
        tmp_obj.update({'sub_smiles': x['sub_smiles']})
        tmp_obj.update({'ref': 'GVK'})

        ad.append(tmp_obj)

    return ad


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()

        # here, one needs to check with the Google ReCaptcha API whether ReCaptcha was sucessfully solved.
        # what would also be needed here is some kind of delay when a certain IP makes too many requests to either
        # signup oder login.

        # check if user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=post_data.get('email')
            ).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get('password')
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[0]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403


class AssayDataAPI(MethodView):
    """
    Assaydata resource
    """

    def __init__(self):
        pass

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')

        print(auth_header)
        args = request.args
        qid = args['qid']

        if auth_header:
            try:
                auth_token = auth_header.split(" ")[0]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                if user.id:
                    responseObject = get_assay_data(qid)

                    return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


class GVKDataAPI(MethodView):
    """
    GVKData resource
    """

    def __init__(self):
        pass

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')

        print(auth_header)
        args = request.args
        qid = args['qid']

        if auth_header:
            try:
                auth_token = auth_header.split(" ")[0]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                if user.id:
                    responseObject = get_gvk_data(qid)

                    return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
assay_data_view = AssayDataAPI.as_view('assay_data_api')
gvk_data_view = GVKDataAPI.as_view('gvk_data_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/assaydata',
    view_func=assay_data_view,
    methods=['GET'],
)
auth_blueprint.add_url_rule(
    '/gvk_data',
    view_func=gvk_data_view,
    methods=['GET'],
)