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


def generate_fingerprint(smiles, compound_id, main_label, qid):
    if smiles:
        compound = Compound(compound_string=smiles, identifier_type='smiles', suppress_hydrogens=True)
        fingerprint = compound.get_bitmap_fingerprint()
        fp = {x for x in str(fingerprint)[1:-1].split(', ')}

        # if only compound id is set as a label, try to set something more useful
        if compound_id in compound_id_fp_map:
            sim_item = compound_id_fp_map[compound_id]
            if sim_item[1] == compound_id:
                sim_item[1] = main_label
        else:
            compound_id_fp_map.update({compound_id: (compound_id, main_label, qid, fp)})

        return list(fp)
    else:
        return []


def update_es(data, index='reframe'):
    tmp_data = copy.deepcopy(data)
    ikey = tmp_data['ikey']
    if es.exists(index=index, doc_type='compound', id=ikey):
        # for k, v in data.items():
        #     if (type(v) == list or type(v) == dict) and len(v) == 0:
        #         del tmp_data[k]
        #     elif not v:
        #         del tmp_data[k]

        es.update(index=index, id=ikey, doc_type='compound', body={'doc': tmp_data})
    else:
        try:
            # if index does not yet exist, make sure that all fields are being added
            res = es.index(index=index, doc_type='compound', id=ikey, body=data)

        except RequestError as e:
            print(tmp_obj)


def desalt_compound(smiles):
    desalted_smiles = []
    desalted_ikeys = []
    if smiles:
        for single_compound in smiles.split('.'):
            desalted_smiles.append(single_compound)
            try:
                compound = Compound(compound_string=single_compound, identifier_type='smiles')
                ikey = compound.get_inchi_key()
                desalted_ikeys.append(ikey)
            except Exception as e:
                desalted_ikeys.append('')

    return desalted_smiles, desalted_ikeys


def get_rfm_ids(ikey):
    rfm_ids = []
    chem_vendors = []

    for k, v in rfm_ikey_map.items():
        s_id, s_vendor, s_vendor_id = v
        if s_id == ikey:
            rfm_ids.append(k)
            chem_vendors.append({'chem_vendor': s_vendor if pd.notnull(s_vendor) else '',
                                 'chem_vendor_id': s_vendor_id if pd.notnull(s_vendor_id) else ''})

    return rfm_ids, chem_vendors


def calculate_tanimoto(fp_1, fp_2):
    intersct = fp_1.intersection(fp_2)
    return len(intersct)/(len(fp_1) + len(fp_2) - len(intersct))


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

    'reframe_id': [],

    'chem_vendors': [],

    'qid': '',

    'alt_id': '',

    'fingerprint': [],

    'similar_compounds': [],

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
vendor_dt = pd.read_csv(os.path.join(data_dir, 'portal_info_annot.csv'), sep=',')

ikey_wd_map = wdi.wdi_helpers.id_mapper('P235')
compound_id_fp_map = {}

rfm_ikey_map = {x['public_id']: (x['ikey'], x['library'], x['source_id']) for x in
                vendor_dt[['public_id', 'ikey', 'library', 'source_id']].to_dict(orient='records')}

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
    tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)

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
        smiles = tmp_obj['gvk']['smiles']
        main_label = tmp_obj['gvk']['drug_name'][0] if len(tmp_obj['gvk']['drug_name']) > 0 else ikey
        tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
        d_smiles, d_ikey = desalt_compound(smiles)
        if len(d_smiles) > 1:
            tmp_obj['sub_smiles'] = d_smiles
            tmp_obj['sub_ikey'] = d_ikey

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
    tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)

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
        smiles = tmp_obj['integrity']['smiles']
        main_label = tmp_obj['integrity']['drug_name'][0] if len(tmp_obj['integrity']['drug_name']) > 0 else ikey
        tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
        d_smiles, d_ikey = desalt_compound(smiles)
        if len(d_smiles) > 1:
            tmp_obj['sub_smiles'] = d_smiles
            tmp_obj['sub_ikey'] = d_ikey

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
    tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)

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
        smiles = tmp_obj['informa']['smiles']
        main_label = tmp_obj['informa']['drug_name'][0] if len(tmp_obj['informa']['drug_name']) > 0 else ikey
        tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
        d_smiles, d_ikey = desalt_compound(smiles)
        if len(d_smiles) > 1:
            tmp_obj['sub_smiles'] = d_smiles
            tmp_obj['sub_ikey'] = d_ikey

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

    tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)

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

for c, (compound_id, values) in enumerate(compound_id_fp_map.items()):
    _, main_label, qid, fp = values

    found_cmpnds = []
    for r_id, (_, r_label, r_qid, r_fp) in compound_id_fp_map.items():
        if compound_id == r_id:
            continue

        tnmt = calculate_tanimoto(fp, r_fp)
        if tnmt > 0.85:
            search_result = {'compound_id': r_id, 'qid': r_qid, 'score': tnmt, 'main_label': r_label}
            found_cmpnds.append(search_result)

    found_cmpnds.sort(key=lambda x: x['score'], reverse=True)

    if len(found_cmpnds) > 0:
        print(found_cmpnds)

    sim_obj = {
        'ikey': compound_id,
        'similar_compounds': found_cmpnds
    }

    if len(found_cmpnds) > 0:
        update_es(sim_obj, index='similarity')

    if c % 100 == 0:
        print(c)


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

