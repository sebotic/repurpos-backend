# project/server/auth/views.py


from flask import Blueprint, request, make_response, jsonify, session
from flask.views import MethodView

import json as json

from project.server import bcrypt, db
from project.server.models import User, BlacklistToken

import pandas as pd
import wikidataintegrator as wdi
import requests
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
es = Elasticsearch()

from data.example_data import example_data

auth_blueprint = Blueprint('auth', __name__)


assay_descrip = pd.read_csv(data_dir + '20180222_assay_descriptions.csv')

plot_data = pd.read_csv(data_dir + '20180222_EC50_DATA_RFM_IDs_cpy.csv')

# data_dir = os.getenv('DATA_DIR')
#
# assay_data = pd.read_csv(data_dir + 'reframe_short_20170822.csv')
# gvk_dt = pd.read_csv(data_dir + 'gvk_data_to_release.csv')
# integrity_dt = pd.read_csv(data_dir + 'integrity_annot_20171220.csv')
#
# informa_dt = pd.read_csv(data_dir + 'informa_annot_20171220.csv')
#

ikey_wd_map = wdi.wdi_helpers.id_mapper('P235')
wd_ikey_map = dict(zip(ikey_wd_map.values(), ikey_wd_map.keys()))

print('wd ikey map length:', len(wd_ikey_map))
#
#
# def get_assay_data(qid):
#     tmp_dt = assay_data.loc[assay_data['wikidata'] == qid, :]
#
#     ad = list()
#
#     for c, x in tmp_dt.iterrows():
#         tmp_obj = dict()
#
#         # for k in x.keys():
#         #     tmp_obj.update({k: x[k]})
#
#         # only return the data really necessary for being rendered
#         datamode = x['datamode']
#
#         if datamode not in ['DECREASING', 'INCREASING', 'SUPER_ACTIVE']:
#             continue
#         elif datamode == 'DECREASING':
#             tmp_obj.update({'activity_type': 'IC50'})
#         elif datamode == 'INCREASING':
#             tmp_obj.update({'activity_type': 'EC50'})
#         elif datamode == 'SUPER_ACTIVE':
#             tmp_obj.update({'activity_type': 'SUPER ACTIVE'})
#
#         tmp_obj.update({'ac50': round(x['ac50'], 10)})
#         tmp_obj.update({'assay_title': x['assay_title']})
#         tmp_obj.update({'smiles': x['smiles']})
#         tmp_obj.update({'PubChem CID': str(x['PubChem CID'])})
#         tmp_obj.update({'wikidata': x['wikidata']})
#         tmp_obj.update({'calibr_id': x['calibr_id']})
#         tmp_obj.update({'inchi_key': x['inchi_key']})
#         tmp_obj.update({'ref': 'Calibr'})
#
#         ad.append(tmp_obj)
#
#     return ad
#
#
# def get_gvk_data(qid):
#     ikey = wd_ikey_map[qid]
#     print(ikey)
#
#     ad = list()
#
#     for c, x in gvk_dt.loc[gvk_dt['ikey'] == ikey, :].iterrows():
#         tmp_obj = {
#             'drug_name': x['drug_name'],
#             'phase': [{'label': y, 'qid': '', 'ref': 'GVK'} for y in x['phase'].split('; ')] if pd.notnull(x['phase']) else [],
#             'drug_roa': [{'label': y, 'qid': '', 'ref': 'GVK'} for y in x['drug_roa'].split('; ')] if pd.notnull(x['drug_roa']) else [],
#             'category': [{'label': y, 'qid': '', 'ref': 'GVK'} for y in x['category'].split('; ')] if pd.notnull(x['category']) else [],
#             'mechanism': [{'label': y, 'qid': '', 'ref': 'GVK'} for y in x['mechanism'].split('; ')] if pd.notnull(x['mechanism']) else [],
#             'synonyms': [{'label': y, 'qid': '', 'ref': 'GVK'} for y in x['synonyms'].split('; ')] if pd.notnull(x['synonyms']) else [],
#             'sub_smiles': x['sub_smiles'],
#         }
#
#         for cc, i in integrity_dt.loc[integrity_dt['ikey'] == ikey, :].iterrows():
#             if pd.notnull(i['status']):
#                 tmp_obj['phase'].extend(
#                     [{'label': y, 'qid': '', 'ref': 'Integrity'} for y in i['status'].split('; ')])
#             if pd.notnull(i['int_thera_group']):
#                 tmp_obj['category'].extend(
#                     [{'label': y, 'qid': '', 'ref': 'Integrity'} for y in i['int_thera_group'].split('; ')])
#             if pd.notnull(i['int_MoA']):
#                 tmp_obj['mechanism'].extend(
#                     [{'label': y, 'qid': '', 'ref': 'Integrity'} for y in i['int_MoA'].split('; ')])
#
#         for cc, i in informa_dt.loc[informa_dt['ikey'] == ikey, :].iterrows():
#             if pd.notnull(i['Global Status']):
#                 tmp_obj['phase'].extend(
#                     [{'label': y, 'qid': '', 'ref': 'Informa'} for y in i['Global Status'].split('; ')])
#             # if pd.notnull(i['int_thera_group']):
#                 # tmp_obj['category'].extend(
#                 #     [{'label': y, 'qid': '', 'ref': 'Informa'} for y in i['int_thera_group'].split('; ')])
#             if pd.notnull(i['Mechanism Of Action']):
#                 tmp_obj['mechanism'].extend(
#                     [{'label': y, 'qid': '', 'ref': 'Informa'} for y in i['Mechanism Of Action'].split('; ')])
#
#         ad.append(tmp_obj)
#
#     print(ad)
#
#     return ad

# --- LDH ---
def get_assay_details(assay_id):
    organisms = ['C. parvum', 'C. hominis', 'M. tuberculosis', 'Wolbachia', 'P. falciparum', 'Cryptosporidium', 'in vitro', 'in vivo', 'Mycobacterium tuberculosis', 'M. smegmatis']
    # def
    filtered = assay_descrip[assay_descrip.assay_id == assay_id].reset_index()

    # format the text
    filtered.assay_type = filtered.assay_type.apply(lambda x: x.lower())
    filtered.detection_method = filtered.detection_method.apply(lambda x: x.lower())
    filtered.drug_conc = filtered.drug_conc.apply(lambda x: x.replace('uM', ' µM'))

    return filtered


def get_assay_list():
    assays = []

    for idx, assay in assay_descrip.sort_values(['indication', 'assay_type', 'title']).iterrows():
        temp = {
        'assay_id': assay.assay_id,
        'title': assay.title,
        'indication': assay.indication,
        'assay_type': assay.assay_type,
        'summary':  assay.summary
        }

        assays.append(temp)

    return assays


def get_dotplot_data(aid):
    def find_type(datamode):
        if(datamode.lower() == 'decreasing'):
            return 'IC'
        elif(datamode.lower() == 'increasing'):
            return 'EC'
        else:
            return 'unknown'

    def find_name(row):
        if(pd.isnull(row.pubchem_label)):
            return row.ID
        else:
            return row.pubchem_label

    def find_cmpdlink(wikidata_id, url_stub = "/#/compound_data/"):
          # URL stub for individual compound page, e.g. https://repurpos.us/#/compound_data/Q10859697
        if(wikidata_id):
            return url_stub + wikidata_id


    assay_data = []
    # filter out data: selected assay, valid AC50 value
    filtered = plot_data.copy()[(plot_data['id'] == aid) & (plot_data['ac50'])]

    filtered['assay_type'] = filtered.datamode.apply(find_type)
    filtered = filtered.loc[filtered['assay_type'] != 'unknown'] # remove weird data modes

    filtered['url'] = filtered.wikidata.apply(find_cmpdlink)
    filtered['name'] = filtered.apply(find_name, axis = 1)

    # group by unique ID and nest.
    # fncns = ['count', 'min', 'max', 'mean']
    # filtered = filtered.groupby(['ID']).agg(fncns)

    # sort values
    filtered = filtered.sort_values('ac50')

    # convert to the proper json-able structure
    for idx, cmpd in filtered.iterrows():
        temp = {
        'assay_title': cmpd.assay_title,
        'calibr_id': cmpd.calibr_id,
        'name': cmpd.pc,
        'ac50': cmpd.ac50,
        'assay_type': cmpd.assay_type,
        'efficacy': cmpd.efficacy,
        'r_sq': cmpd.rsquared,
        'pubchem_id': cmpd['PubChem CID'],
        'url': cmpd.url
        }

        assay_data.append(temp)

    return assay_data


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

        recaptcha_token = post_data.get('recaptcha_token')
        params = {
            'secret': os.getenv('RECAPTCHA_SECRET_KEY'),
            'response': recaptcha_token
        }

        r = requests.post('https://www.google.com/recaptcha/api/siteverify', params=params).json()
        print(r)

        try:
            if not r['success']:
                response_object = {
                    'status': 'fail',
                    'message': 'ReCaptcha token could not be verified!'
                }
                return make_response(jsonify(response_object)), 401
        except KeyError:
            response_object = {
                'status': 'fail',
                'message': 'Some error occurred verifying ReCaptcha'
            }
            return make_response(jsonify(response_object)), 401

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
            auth_token = auth_header.split(" ")[0]
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


# class AssayDataAPI(MethodView):
#     """
#     Assaydata resource
#     """
#
#     def __init__(self):
#         pass
#
#     def get(self):
#         # get the auth token
#         auth_header = request.headers.get('Authorization')
#
#         print(auth_header)
#         args = request.args
#         qid = args['qid']
#
#         if auth_header:
#             try:
#                 auth_token = auth_header.split(" ")[0]
#             except IndexError:
#                 responseObject = {
#                     'status': 'fail',
#                     'message': 'Bearer token malformed.'
#                 }
#                 return make_response(jsonify(responseObject)), 401
#         else:
#             auth_token = ''
#         if auth_token:
#             resp = User.decode_auth_token(auth_token)
#             if not isinstance(resp, str):
#                 user = User.query.filter_by(id=resp).first()
#                 if user.id:
#                     responseObject = get_assay_data(qid)
#
#                     return make_response(jsonify(responseObject)), 200
#             responseObject = {
#                 'status': 'fail',
#                 'message': resp
#             }
#             return make_response(jsonify(responseObject)), 401
#         else:
#             responseObject = {
#                 'status': 'fail',
#                 'message': 'Provide a valid auth token.'
#             }
#             return make_response(jsonify(responseObject)), 401
#
#
# class GVKDataAPI(MethodView):
#     """
#     GVKData resource
#     """
#
#     def __init__(self):
#         pass
#
#     def get(self):
#         # get the auth token
#         auth_header = request.headers.get('Authorization')
#
#         print(auth_header)
#         args = request.args
#         qid = args['qid']
#
#         if auth_header:
#             try:
#                 auth_token = auth_header.split(" ")[0]
#             except IndexError:
#                 responseObject = {
#                     'status': 'fail',
#                     'message': 'Bearer token malformed.'
#                 }
#                 return make_response(jsonify(responseObject)), 401
#         else:
#             auth_token = ''
#         if auth_token:
#             resp = User.decode_auth_token(auth_token)
#             if not isinstance(resp, str):
#                 user = User.query.filter_by(id=resp).first()
#                 if user.id:
#                     responseObject = get_gvk_data(qid)
#
#                     return make_response(jsonify(responseObject)), 200
#             responseObject = {
#                 'status': 'fail',
#                 'message': resp
#             }
#             return make_response(jsonify(responseObject)), 401
#         else:
#             responseObject = {
#                 'status': 'fail',
#                 'message': 'Provide a valid auth token.'
#             }
#             return make_response(jsonify(responseObject)), 401


class SearchAPI(MethodView):
    """
    Search with elasticsearch
    """

    def __init__(self):
        pass

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')

        print(auth_header)
        args = request.args
        search_term = args['search']

        body = {
            "from": 0, "size": 100,
            "query": {
                "query_string": {

                    "query": "{}*".format(search_term)
                }
            }
        }

        try:

            res = es.search(index="reframe", body=body)
        except Exception as e:
            return make_response(jsonify({'status': 'fail', 'ikeys': []})), 500

        ikeys = []
        for x in res['hits']['hits']:
            ikeys.append(x['_id'])

        responseObject = {
            'status': 'success',
            'ikeys': ikeys
        }

        return make_response(jsonify(responseObject)), 200




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



class DataAPI(MethodView):
    """
    Data resource
    """

    def __init__(self):
        pass

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')

        print(auth_header)
        args = request.args
        qid = args['qid']
        ikey = wd_ikey_map[qid]
        print(qid, ikey)

        try:
            res = es.get(index="reframe", doc_type='compound', id=ikey)
        except Exception as e:
            if qid in example_data:
                response_object = {qid: example_data[qid], "status": "success"}
                return make_response(jsonify(response_object)), 200
            else:
                return make_response(jsonify({'status': 'fail', 'ikeys': []})), 500


        responseObject = {
            'status': 'success',
            qid: res['_source']
        }

        return make_response(jsonify(responseObject)), 200


# --- LDH ---
class AssayListAPI(MethodView):
    """
    Assay list resource
    """

    def __init__(self):
        pass

    def get(self):
        responseObject = get_assay_list()

        return make_response(jsonify(responseObject)), 200

# TODO: need a check if data returns something?
class AssayDetailsAPI(MethodView):
    """
    Assay description resource
    """

    def __init__(self):
        pass

    def get(self):
        args = request.args
        aid = args['aid']

        responseObject = get_assay_details(aid)
        return make_response(responseObject.to_json(orient="records")), 200

class PlotDataAPI(MethodView):
    """
    Assay list resource
    """

    def __init__(self):
        pass

    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')

        print(auth_header)
        args = request.args
        aid = args['aid']

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
                    responseObject = get_dotplot_data(aid)

# !! WARNING: jsonify can't handle NaN, since JSON hates NaN.

                    # responseObject = [{
                    #     "ac50": 1.25e-08,
                    #     "assay_title": "Crypto-C. parvum HCI proliferation assay - Wild Cp",
                    #     "assay_type": "IC",
                    #     "efficacy": -104.54743959999999,
                    #     "name": "drug891",
                    #     "pubchem_id": "CID2722",
                    #     "r_sq": 0.9641395209999999,
                    #     "test": "test",
                    #     "url": "/#/compound_data/Q239569"
                    # },
                    #     {
                    #     "ac50": 4.5199999999999994e-08,
                    #     "assay_title": "Crypto-C. parvum HCI proliferation assay - Wild Cp",
                    #     "assay_type": "IC",
                    #     "efficacy": -100.0,
                    #     "name": "drug888",
                    #     "pubchem_id": "CID2722",
                    #     "r_sq": 0.682526052,
                    #     "test": "test",
                    #     "url": "/#/compound_data/Q239569"
                    # }]


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

# --- LDH ---
assay_list_view = AssayListAPI.as_view('assay_list_api')
assay_details_view = AssayDetailsAPI.as_view('assay_details_api')
plot_data_view = PlotDataAPI.as_view('plot_data_api')
# -----------

# assay_data_view = AssayDataAPI.as_view('assay_data_api')
# gvk_data_view = GVKDataAPI.as_view('gvk_data_api')
search_view = SearchAPI.as_view('search_api')
data_view = DataAPI.as_view('data_api')

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
# auth_blueprint.add_url_rule(
#     '/assaydata',
#     view_func=assay_data_view,
#     methods=['GET'],
# )
# auth_blueprint.add_url_rule(
#     '/gvk_data',
#     view_func=gvk_data_view,
#     methods=['GET'],
# )
auth_blueprint.add_url_rule(
    '/search',
    view_func=search_view,
    methods=['GET'],
)
auth_blueprint.add_url_rule(
    '/data',
    view_func=data_view,
    methods=['GET'],
)
# --- assay lists (LDH) ---
auth_blueprint.add_url_rule(
    '/assay_list',
    view_func=assay_list_view,
    methods=['GET'],
)
auth_blueprint.add_url_rule(
    '/assay_details',
    view_func=assay_details_view,
    methods=['GET'],
)
auth_blueprint.add_url_rule(
    '/assaydata_plot',
    view_func=plot_data_view,
    methods=['GET'],
)
