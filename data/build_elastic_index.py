# from cdk_pywrapper.cdk_pywrapper import Compound

import pandas as pd
import copy
import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
es = Elasticsearch()



# test_inchi = 'InChI=1S/C23H18ClF2N3O3S/c1-2-9-33(31,32)29-19-8-7-18(25)20(21(19)26)22(30)17-12-28-23-16(17)10-14(11-27-23)13-3-5-15(24)6-4-13/h3-8,10-12,29H,2,9H2,1H3,(H,27,28)'
# cmpnd = Compound(compound_string=test_inchi, identifier_type='inchi')
# print(cmpnd.get_inchi_key())

# index name 'reframe'

gvk_doc_map = {
    'hvac_id': 'hvac_id',
    'gvk_id': 'gvk_id',
    'calibr_note': None,
    'drug_name': 'drug_name',
    'phase': ('phase', '; '),
    'drug_roa': ('roa', '; '),
    'category': ('category', '; '),
    'mechanism': ('mechanism', '; '),
    'sub_smiles': 'smiles',
    'synonyms':	('synonyms', '; '),
    'ikey': 'ikey'
}

integrity_doc_map = {
    'id': 'id',
    'smiles': 'smiles',
    'name': 'drug_name',
    'status': ('phase', '; '),
    'int_thera_group': ('category', '; '),
    'int_MoA': ('mechanism', '; '),
    'calibr_note': None,
    'ikey': 'ikey',
    'wikidata': 'wikidata',
    'PubChem CID': 'PubChem CID'
}

informa_doc_map = {
    'Drug Name': 'drug_name',
    'Global Status': ('phase', '; '),
    'Highest Phase Reached-Ceased Statuses': 'highest_phase',
    'Mechanism Of Action': ('mechanism', '; '),
    'Target Name': None,
    'Target Families': None,
    'Origin': None,
    'Chemical Name': None,
    'Chemical structure (SMILES format)': 'smiles',
    'Drug Key (Unique ID)': None,
    'ikey': 'ikey',
    'PubChem CID': 'PubChem CID',
    'wikidata': 'wikidata',
}

assay_data_doc_map = {
    'substring': None,
    'calibr_id': 'id',
    'ac50': 'ac50',
    'datamode': 'datamode',
    'genedata_id': None,
    'assay_title': 'assay_title',
    'smiles': 'smiles',
    'inchi_key': 'ikey',
    'PubChem CID': 'PubChem CID',
    'PubChem lable': None,
    'wikidata': 'wikidata'
}

reframe_doc = {
    'ikey': '',

    'gvk': {

    },
    'integrity': {

    },
    'informa': {

    },
    'assay': []

}

basic_block = {
    'id': None,
    'phase': [],
    'mechanism': [],
    'category': []
}

data_dir = os.getenv('DATA_DIR')
assay_data = pd.read_csv(data_dir + 'reframe_short_20170822.csv')
gvk_dt = pd.read_csv(data_dir + 'gvk_data_to_release.csv')
integrity_dt = pd.read_csv(data_dir + 'integrity_annot_20171220.csv')
informa_dt = pd.read_csv(data_dir + 'informa_annot_20171220.csv')

for c, x in gvk_dt.iterrows():
    ikey = x['ikey']
    if pd.isnull(ikey):
        continue

    tmp_obj = copy.copy(reframe_doc)
    tmp_obj['ikey'] = ikey

    for k, v in gvk_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['gvk'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['gvk'].update({v: x[k]})

    # print(tmp_obj)

    try:
        res = es.index(index="reframe", doc_type='compound', id=ikey, body=tmp_obj)

    except RequestError as e:
        print(tmp_obj)
        break

    # if c > 20:
    #     break

    if c % 100 == 0:
        print(c)

for c, x in integrity_dt.iterrows():
    ikey = x['ikey']
    if pd.isnull(ikey):
        continue

    tmp_obj = copy.copy(reframe_doc)
    tmp_obj['ikey'] = ikey

    for k, v in integrity_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['integrity'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['integrity'].update({v: x[k]})

    if es.exists(index='reframe', doc_type='compound', id=ikey):
        # print('this exists!!')
        es.update(index='reframe', id=ikey, doc_type='compound', body={'doc': {'integrity': tmp_obj['integrity']}})
    else:
        try:
            res = es.index(index="reframe", doc_type='compound', id=ikey, body=tmp_obj)

        except RequestError as e:
            print(tmp_obj)
            break

    if c % 100 == 0:
        print(c)


for c, x in informa_dt.iterrows():
    ikey = x['ikey']
    if pd.isnull(ikey):
        continue

    tmp_obj = copy.copy(reframe_doc)
    tmp_obj['ikey'] = ikey

    for k, v in informa_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['informa'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['informa'].update({v: x[k]})

    if es.exists(index='reframe', doc_type='compound', id=ikey):
        # print('this exists!!')
        es.update(index='reframe', id=ikey, doc_type='compound', body={'doc': {'informa': tmp_obj['informa']}})
    else:
        try:
            res = es.index(index="reframe", doc_type='compound', id=ikey, body=tmp_obj)

        except RequestError as e:
            print(tmp_obj)
            break

    if c % 100 == 0:
        print(c)

for i in assay_data['inchi_key'].unique():
    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = i
    ikey = i
    print(i)

    if pd.isnull(ikey):
        continue

    for c, x in assay_data.loc[assay_data['inchi_key'] == i, :].iterrows():

        tt = {}

        for k, v in assay_data_doc_map.items():
            if pd.isnull(x[k]) or v is None:
                continue

            if k == 'datamode':
                datamode = x['datamode']
                if datamode not in ['DECREASING', 'INCREASING', 'SUPER_ACTIVE']:
                    continue
                elif datamode == 'DECREASING':
                    tt.update({'activity_type': 'IC50'})
                elif datamode == 'INCREASING':
                    tt.update({'activity_type': 'EC50'})
                elif datamode == 'SUPER_ACTIVE':
                    tt.update({'activity_type': 'SUPER ACTIVE'})

                continue

            tt.update({v: x[k]})

        tmp_obj['assay'].append(tt)

    # print(tmp_obj['assay'])

    if es.exists(index='reframe', doc_type='compound', id=ikey):
        # print('this exists!!')
        es.update(index='reframe', id=ikey, doc_type='compound', body={'doc': {'assay': tmp_obj['assay']}})
    else:
        try:
            res = es.index(index="reframe", doc_type='compound', id=ikey, body=tmp_obj)

        except RequestError as e:
            print(tmp_obj)
            break

    # if c % 100 == 0:
    #     print(c)

body = {
    "query": {
        "query_string": {

            "query": "phase*"
        }
    }
}

es.indices.refresh(index="reframe")

r = es.search(index="reframe", body=body)
print(r)

# generate example_data.py


qids = ["Q27286421", "Q27088554", "Q27291538", "Q27077191", "Q15411004"]
ikeys = ['WXNRAKRZUCLRBP-UHFFFAOYSA-N',
         'NNBGCSGCRSCFEA-UHFFFAOYSA-N',
         'MPMZSZMDCRPSRF-UHFFFAOYSA-N',
         'ONPGOSVDVDPBCY-CQSZACIVSA-N',
         'WXJFKKQWPMNTIM-VWLOTQADSA-N'
         ]

example_data = {}

for c, x in enumerate(qids):
    r = es.get(index="reframe", doc_type='compound', id=ikeys[c])['_source']
    example_data.update({x: r})

with open('example_data.json', 'w') as outfile:
    json.dump(example_data, outfile)
