# from cdk_pywrapper.cdk_pywrapper import Compound

import pandas as pd
import copy
import json
import os

import wikidataintegrator as wdi
from cdk_pywrapper.cdk_pywrapper import Compound

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
es = Elasticsearch()


# test_inchi = 'InChI=1S/C23H18ClF2N3O3S/c1-2-9-33(31,32)29-19-8-7-18(25)20(21(19)26)22(30)17-12-28-23-16(17)10-14(11-27-23)13-3-5-15(24)6-4-13/h3-8,10-12,29H,2,9H2,1H3,(H,27,28)'
# cmpnd = Compound(compound_string=test_inchi, identifier_type='inchi')
# print(cmpnd.get_inchi_key())

def generate_fingerprint(smiles):
    if smiles:
        compound = Compound(compound_string=smiles, identifier_type='smiles')
        fingerprint = compound.get_bitmap_fingerprint()
        fp = {x for x in str(fingerprint)[1:-1].split(', ')}
        return list(fp)
    else:
        return []


def update_es(data):
    tmp_data = copy.deepcopy(data)
    if es.exists(index='reframe', doc_type='compound', id=ikey):
        for k, v in data.items():
            if (type(v) == list or type(v) == dict) and len(v) == 0:
                del tmp_data[k]
            elif not v:
                del tmp_data[k]

        es.update(index='reframe', id=ikey, doc_type='compound', body={'doc': tmp_data})
    else:
        try:
            # if index does not yet exist, make sure that all fields are being added
            res = es.index(index="reframe", doc_type='compound', id=ikey, body=data)

        except RequestError as e:
            print(tmp_obj)


# index name 'reframe'

gvk_doc_map = {
    # 'hvac_id': 'hvac_id',
    'gvk_id': 'gvk_id',
    # 'calibr_note': None,
    'drug_name': ('drug_name', '; '),
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
    'name': ('drug_name', '; '),
    'status': ('phase', '; '),
    'int_thera_group': ('category', '; '),
    'int_MoA': ('mechanism', '; '),
    # 'calibr_note': None,
    'ikey': 'ikey',
    'wikidata': 'wikidata',
    'PubChem CID': 'PubChem CID'
}

informa_doc_map = {
    'name': ('drug_name', '\n'),
    # 'Global Status': ('phase', '; '),
    'highest_status (between global and Highest Status)': 'highest_phase',
    'moa': ('mechanism', '\n'),
    'target_name': ('target_name', '\n'),
    'target_family': ('target_families', '\n'),
    'origin': 'origin',
    'chem_name': 'chemical_name',
    'smiles': 'smiles',
    'key': None,
    'ikey': 'ikey',
    'pubchem': 'PubChem CID',
    'wikidata': 'wikidata',
    'informa_id': 'informa_id'
}

assay_data_doc_map = {
    'calibr_id': 'reframe_id',
    'ac50': 'ac50',
    'datamode': 'datamode',
    'genedata_id': 'assay_id',
    'assay_title': 'assay_title',
    # 'smiles': 'smiles',
    'ikey': 'ikey',
    'PubChem CID': 'PubChem CID',
    'pubchem_label': 'pubchem_label',
    'wikidata': 'wikidata',
    'library': 'chem_vendor',
    'source_id': 'chem_vendor_id'

}

reframe_doc = {
    'ikey': '',

    'reframe_id': '',

    'qid': '',

    'alt_id': '',

    'fingerprint': [],

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
# assay_data = pd.read_csv(os.path.join(data_dir, 'reframe_short_20170822.csv'))
gvk_dt = pd.read_csv(os.path.join(data_dir, '20180430_GVK_excluded_column.csv'))
integrity_dt = pd.read_csv(os.path.join(data_dir, 'integrity_annot_20180504.csv'))
informa_dt = pd.read_csv(os.path.join(data_dir, '20180430_Informa_excluded_column.csv'))

assay_descr = pd.read_csv(os.path.join(data_dir, '20180222_assay_descriptions.csv'), header=0)
assay_data = pd.read_csv(os.path.join(data_dir, 'assay_data_w_vendor_mapping.csv'), header=0)
# vendor_dt = pd.read_csv(os.path.join(data_dir, 'portal_info_annot.csv'), sep='|')

ikey_wd_map = wdi.wdi_helpers.id_mapper('P235')

for c, x in gvk_dt.iterrows():
    if x['exclude'] == 1:
        continue

    ikey = x['ikey']
    if pd.isnull(ikey):
        if pd.notnull(x['gvk_id']):
            ikey = str(x['gvk_id'])
        else:
            continue

    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = ikey

    if ikey in ikey_wd_map:
        tmp_obj['qid'] = ikey_wd_map[ikey]

    for k, v in gvk_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['gvk'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['gvk'].update({v: x[k]})

    if 'smiles' in tmp_obj['gvk']:
        tmp_obj['fingerprint'] = generate_fingerprint(tmp_obj['gvk']['smiles'])

    update_es(tmp_obj)

    # if c > 20:
    #     break

    if c % 100 == 0:
        print(c)

for c, x in integrity_dt.iterrows():
    if x['exclude'] == 1:
        continue

    ikey = x['ikey']
    if pd.isnull(ikey):
        if pd.notnull(x['id']):
            ikey = str(x['id'])
        else:
            continue

    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = ikey

    if ikey in ikey_wd_map:
        tmp_obj['qid'] = ikey_wd_map[ikey]

    for k, v in integrity_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['integrity'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['integrity'].update({v: x[k]})

    if 'smiles' in tmp_obj['integrity']:
        tmp_obj['fingerprint'] = generate_fingerprint(tmp_obj['integrity']['smiles'])

    update_es(tmp_obj)

    if c % 100 == 0:
        print(c)


for c, x in informa_dt.iterrows():
    if x['exclude'] == 1:
        continue

    ikey = x['ikey']
    if pd.isnull(ikey):
        if pd.notnull(x['informa_id']):
            ikey = str(x['informa_id'])
        else:
            continue

    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = ikey

    if ikey in ikey_wd_map:
        tmp_obj['qid'] = ikey_wd_map[ikey]

    for k, v in informa_doc_map.items():
        if pd.isnull(x[k]) or v is None:
            continue
        if type(v) == tuple:
            tmp_obj['informa'].update({v[0]: x[k].split(v[1])})

        else:
            tmp_obj['informa'].update({v: x[k]})

    if 'smiles' in tmp_obj['informa']:
        tmp_obj['fingerprint'] = generate_fingerprint(tmp_obj['informa']['smiles'])

    update_es(tmp_obj)

    if c % 100 == 0:
        print(c)

for i in assay_data['ikey'].unique():
    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = i
    ikey = i
    print(i)

    if ikey in ikey_wd_map:
        tmp_obj['qid'] = ikey_wd_map[ikey]

    if pd.isnull(ikey):
        continue

    for c, x in assay_data.loc[assay_data['ikey'] == i, :].iterrows():

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

    update_es(tmp_obj)

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

