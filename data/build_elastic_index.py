import pandas as pd
import copy
import json
import os
import sys
import pprint

import wikidataintegrator as wdi
from cdk_pywrapper.cdk_pywrapper import Compound

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
es = Elasticsearch()


def generate_fingerprint(smiles, compound_id, main_label, qid):
    if smiles:
        try:
            compound = Compound(compound_string=smiles, identifier_type='smiles', suppress_hydrogens=True)
            fingerprint = compound.get_bitmap_fingerprint()
        except ValueError as e:
            print('Failed for', smiles, compound_id, main_label, qid)
            print(e)
            return []
        fp = {x for x in str(fingerprint)[1:-1].split(', ')}

        # if only compound id is set as a label, try to set something more useful
        if compound_id in compound_id_fp_map:
            sim_item = compound_id_fp_map[compound_id]
            if sim_item[1] == compound_id:
                sim_item[1] = main_label
        else:
            compound_id_fp_map.update({compound_id: [compound_id, main_label, qid, fp]})

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
    desalted_weights = []
    if smiles:
        for single_compound in smiles.split('.'):
            desalted_smiles.append(single_compound)
            try:
                compound = Compound(compound_string=single_compound, identifier_type='smiles')
                ikey = compound.get_inchi_key()
                desalted_ikeys.append(ikey)
                desalted_weights.append(float(compound.get_molecular_weight()))
            except Exception as e:
                print('Inchi conversion failed', smiles)
                desalted_ikeys.append('')
                desalted_weights.append(0)

    return desalted_smiles, desalted_ikeys, desalted_weights


def get_rfm_ids(ikey):
    rfm_ids = []
    chem_vendors = []
    match_types = []

    if ikey not in vendor_dt.ikey.values:
        return rfm_ids, chem_vendors, match_types

    tdf = vendor_dt.loc[vendor_dt.ikey == ikey, :]
    rfm_ids = list(tdf.public_id.values)
    # add to list of all data vendor associated RFM ids.
    covered_rfm_ids.update(rfm_ids)
    chem_vendors = [{'chem_vendor': x['library'] if pd.notnull(x['library']) else '',
                     'chem_vendor_id': x['source_id'] if pd.notnull(x['source_id']) else ''}
                    for x in tdf[['library', 'source_id']].to_dict('records')]
    match_types = list(tdf.rfm_match_type.values)

    # for k, v in rfm_ikey_map.items():
    #     s_id, s_vendor, s_vendor_id, s_match_type = v
    #     if s_id == ikey:
    #         rfm_ids.append(True)
    #         chem_vendors.append({'chem_vendor': s_vendor if pd.notnull(s_vendor) else '',
    #                              'chem_vendor_id': s_vendor_id if pd.notnull(s_vendor_id) else ''})
    #
    #         match_types.append(s_match_type)

    return rfm_ids, chem_vendors, match_types


def calculate_tanimoto(fp_1, fp_2):
    intersct = fp_1.intersection(fp_2)
    return len(intersct)/(len(fp_1) + len(fp_2) - len(intersct))


def add_to_no_charge_list(ikey):
    sub_ikey = ikey[:25]
    if sub_ikey in no_charge_map:
        no_charge_map[sub_ikey].append(ikey)
    else:
        no_charge_map.update({sub_ikey: [ikey]})


def to_ikey(smiles):
    compound = Compound(compound_string=smiles, identifier_type='smiles')
    return compound.get_inchi_key()


def get_qid(annotations):
    annot_qid_lst = []
    for a in annotations:
        if a in annotation_mappings['annotation string (original)'].values:
            qids = annotation_mappings.loc[annotation_mappings['annotation string (original)'] == a, 'WD item'].values[0]
            #split_labels = annotation_mappings.loc[annotation_mappings['annotation_string_split'] == a, 'WD item'].values[0]
            # annot_qid_lst.append({
            #     'label': split_labels.split('|') if pd.notnull(split_labels) else [a],
            #     'wikidata': [] if pd.isnull(qids) else qids.split('|')
            # })
            annot_qid_lst.append({
                'label': a,
                'wikidata': qids if pd.notnull(qids) else ''
            })
        else:
            annot_qid_lst.append({
                'label': a,
                'wikidata': ''
            })

    return annot_qid_lst


def generate_unifiers(df, smiles_col, vendor_id_col):
    for c, x in df.iterrows():
        ikey = x['ikey']
        smiles = x[smiles_col]  # sub_smiles for GVK!

        if pd.isnull(smiles):
            continue

        smiles = smiles.split(' |')[0]

        if pd.isnull(ikey):
            if pd.notnull(x[vendor_id_col]):
                df.loc[c, 'uikey'] = str(x[vendor_id_col])
                add_to_no_charge_list(df.loc[c, 'uikey'])
                continue
            else:
                continue

        # List of metals, if contained in a SMILES, the SMILES should not be split
        no_split_metals = ['[Zn++]', '[Gd+3]', '[Al+3]', '[Fe+3]', '[Fe+2]', '[Zn++]', '[Zn+2]', '[Sr+2]', 'Sb',
                           '[Pt+2]', '[H][Sr][H]', '[Pt++]', '[Cu++]', '[Fe]', '[Co+3]', '[Au+]', '[Ag+]', 'II',
                           '[Mn++]', '[La+3]', '[IH-]', '[Ga+3]', '[Dy+3]', '[Cu+2]', 'Cu', '[Ce+]', 'O[Al++]',
                           'N[Pt++]N', 'Cl[Pt]Cl', 'Cl[Pt+]', 'CC[Hg+]', '[Li+]']

        d_smiles, d_ikey, d_masses = desalt_compound(smiles)

        if 1 < len(d_smiles) and not any([x in smiles for x in no_split_metals]):
            '''
            do not unify when there are more than 3 compounds in a mixture or
            more than 2 compounds with a molecular weight >=195Da. 
            Also, make sure that only if all subsmiles convert to ikeys, the compound/mixture is unified, otherwise
            there is a substantial risk of secondary comopunds/salts will be unified.
            '''
            if len(d_smiles) > 4 or len([w for w in d_masses if w >= 195]) > 1 or \
                    len([x for x in d_ikey if x]) < len(d_ikey):
                df.loc[c, 'uikey'] = ikey
                df.loc[c, 'usmiles'] = smiles
                add_to_no_charge_list(ikey)
                continue

            d_counts = []
            for ik in d_ikey:

                tmp_salt = salt_frequencies.loc[salt_frequencies['ikey'] == ik, :]
                compound_count = tmp_salt['counts'].sum()
                d_counts.append((ik, compound_count))

            d_ikey_freq = [x for _, x in sorted(zip(d_counts, d_ikey), key=lambda pair: pair[0][1])]
            d_smiles_freq = [x for _, x in sorted(zip(d_counts, d_smiles), key=lambda pair: pair[0][1])]
            d_counts_freq = [x for _, x in sorted(zip(d_counts, d_counts), key=lambda pair: pair[0][1])]
            # d_counts.sort(key=lambda x: x[1])

            d_ikey_mass = [x for _, x in sorted(zip(d_masses, d_ikey), key=lambda pair: pair[0], reverse=True)]
            d_smiles_mass = [x for _, x in sorted(zip(d_masses, d_smiles), key=lambda pair: pair[0], reverse=True)]
            d_counts_mass = [x for _, x in sorted(zip(d_masses, d_counts), key=lambda pair: pair[0], reverse=True)]
            d_masses.sort(reverse=True)

            '''
            if the count differences btw 2 compounds are < 3, take the one with largest mass, else take the one
            with largest frequency.
            '''
            if abs(d_counts_mass[0][1] - d_counts_mass[1][1]) < 3:
                tmp_ikey = d_ikey_mass[0]
                tmp_smiles = d_smiles_mass[0]
            else:
                tmp_ikey = d_ikey_freq[0]
                tmp_smiles = d_smiles_freq[0]

            # tackle special case
            if '[S@@+]' in tmp_smiles and '[O-]' in tmp_smiles:
                tmp_smiles = tmp_smiles.replace('[S@@+]', '[S@@]')
                tmp_smiles = tmp_smiles.replace('[O-]', '=O')

            repl = [('[O-]', '[OH]'), ('[N-]', '[NH]'), ('[n-]', '[nH]')]

            for pattern, replacement in repl:
                tmp_smiles = tmp_smiles.replace(pattern, replacement)
                tmp_ikey = to_ikey(tmp_smiles)

            df.loc[c, 'uikey'] = tmp_ikey
            df.loc[c, 'usmiles'] = tmp_smiles

        else:
            df.loc[c, 'uikey'] = ikey
            df.loc[c, 'usmiles'] = smiles

        add_to_no_charge_list(df.loc[c, 'uikey'])

    return df


def generate_vendor_index(dt, vendor_string, doc_map):
    for counter, uid in enumerate(dt['uikey'].unique()):
        ikey = uid
        if pd.isnull(ikey):
            continue

        # ensure that document resolves to one primary ikey covering all compounds with same skeleton and stereochem
        no_charge_map[ikey[:25]].sort(key=lambda s: s[-1], reverse=True)
        primary_ikey = no_charge_map[ikey[:25]][0]

        tmp_obj = copy.deepcopy(reframe_doc)
        tmp_obj['ikey'] = primary_ikey
        rf, cv, mt = get_rfm_ids(primary_ikey)
        if len(rf) > 0:
            tmp_obj['reframe_id'] = mt
        if len(cv) > 0:
            tmp_obj['chem_vendors'] = cv
        tmp_obj[vendor_string] = []

        if primary_ikey in ikey_wd_map:
            tmp_obj['qid'] = ikey_wd_map[primary_ikey]

        if primary_ikey in ikey_main_label_map:
            tmp_obj['main_label'] = ikey_main_label_map[primary_ikey] \
                if pd.notnull(ikey_main_label_map[primary_ikey]) else ''

        tmp_df = dt.loc[dt['uikey'] == uid]
        # if tmp_df.shape[0] > 1:
        #     print(tmp_df)
        for c, x in tmp_df.iterrows():

            if x['exclude'] == 1:
                continue

            # add desalted smiles to 'root' of document for structure drawing
            if pd.notnull(x['usmiles']):
                if 'smiles' in tmp_obj and tmp_obj['smiles']:
                    pass
                elif 'smiles' not in tmp_obj or not tmp_obj['smiles']:
                    tmp_obj['smiles'] = x['usmiles']

                    try:
                        compound = Compound(compound_string=x['usmiles'], identifier_type='smiles')
                        tmp_obj['chirality'] = compound.get_chirality()
                    except Exception as e:
                        print('Determining chirality failed for', ikey, x['usmiles'])

            single_comp_dict = {}
            for k, v in doc_map.items():
                if pd.isnull(x[k]) or v is None:
                    continue
                if type(v) == tuple:
                    if len(v) == 2:
                        single_comp_dict.update({v[0]: x[k].split(v[1])})
                    elif len(v) == 3:
                        single_comp_dict.update({v[0]: get_qid(x[k].split(v[1]))})

                else:
                    single_comp_dict.update({v: x[k]})

            if 'smiles' in single_comp_dict and single_comp_dict['smiles']:

                smiles = single_comp_dict['smiles']
                main_label = single_comp_dict['drug_name'][0] if 'drug_name' in single_comp_dict \
                                                                 and len(single_comp_dict['drug_name']) > 0 else ikey

                if 'main_label' not in tmp_obj or pd.isnull(tmp_obj['main_label']):
                    tmp_obj['main_label'] = main_label

                # tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])

                fp = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
                if len(fp) > 0:
                    tmp_obj['fingerprint'] = fp

                d_smiles, d_ikey, _ = desalt_compound(smiles.split(' |')[0])
                if len(d_smiles) > 1:
                    single_comp_dict['sub_smiles'] = d_smiles
                    single_comp_dict['sub_ikey'] = d_ikey

            tmp_obj[vendor_string].append(single_comp_dict)

        if counter < 2:
            pprint.pprint(tmp_obj)

        update_es(tmp_obj)

        # pprint.pprint(tmp_obj)

        # if c > 20:
        #     break

        if counter % 100 == 0:
            print(counter)

# index name 'reframe'


"""
The following three maps map vendor data column names to ES document json keys. When there is a tuple in the map, the 
strings from the vendor data need to be split. Element one in the tuple represents the ES document json key name, 
element two the split character. Element three, if present, indicates that each of the strings needs to be mapped to 
a Wikidata QID.
"""
gvk_doc_map = {
    # 'hvac_id': 'hvac_id',
    'gvk_id': 'gvk_id',
    # 'calibr_note': None,
    'drug_name': ('drug_name', '; '),
    'phase': ('phase', '; '),
    'drug_roa': ('roa', '; '),
    'category': ('category', '; ', True),
    'mechanism': ('mechanism', '; ', True),
    'sub_smiles': 'smiles',
    'synonyms':	('synonyms', '; '),
    'ikey': 'ikey'
}

# integrity_doc_map = {
#     'id': 'id',
#     'smiles': 'smiles',
#     'name': ('drug_name', '; '),
#     'status': ('phase', '; '),
#     'int_thera_group': ('category', '; ', True),
#     'int_MoA': ('mechanism', '; ', True),
#     # 'calibr_note': None,
#     'ikey': 'ikey',
#     #'wikidata': 'wikidata',
#     #'PubChem CID': 'PubChem CID'
# }

integrity_doc_map = {
    'integrity_id': 'id',
    'smiles': 'smiles',
    'name': ('drug_name', '; '),
    'status': ('phase', '; '),
    'int_thera_group': ('category', '; ', True),
    'int_MoA': ('mechanism', '; ', True),
    # 'calibr_note': None,
    'ikey': 'ikey',
    #'wikidata': 'wikidata',
    #'PubChem CID': 'PubChem CID'
}

informa_doc_map = {
    'name': ('drug_name', '\n'),
    # 'Global Status': ('phase', '; '),
    'highest_status (between global and Highest Status)': 'highest_phase',
    'moa': ('mechanism', '\n', True),
    'target_name': ('target_name', '\n', True),
    'target_family': ('target_families', '\n', True),
    'origin': 'origin',
    'chem_name': 'chemical_name',
    'smiles': 'smiles',
    # 'key': None,
    'ikey': 'ikey',
    # 'pubchem': 'PubChem CID',
    # 'wikidata': 'wikidata',
    'informa_id': 'informa_id'
}

adis_doc_map = {
    # 'hvac_id': 'hvac_id',
    'adis_id': 'adis_id',
    # 'calibr_note': None,
    'approved_name': ('drug_name', '; '),
    'highest_phase': ('phase', '; '),
    'therapeutic_areas': ('therapeutic_areas', '; '),
    'category': ('category', '; ', True),
    'moa': ('mechanism', '; ', True),
    'full_smiles': 'smiles',
    'alternate_names':	('synonyms', '; '),
    'ikey': 'ikey'
}

assay_data_doc_map = {
    #'calibr_id': 'reframe_id',
    'ac50': 'ac50',
    'ac_precision': 'ac_precision',
    'datamode': 'datamode',
    'assay_id': 'assay_id',
#    'assay title': 'assay_title',
    'efficacy': 'efficacy',
    'rsquared': 'rsquared',
    # 'smiles': 'smiles',
    'ikey': 'ikey',
    # 'PubChem CID': 'PubChem CID',
    # 'pubchem_label': 'pubchem_label',
    'wikidata': 'wikidata',
    # 'library': 'chem_vendor',
    # 'source_id': 'chem_vendor_id'
    'fixed_smiles': 'smiles'

}

reframe_doc = {
    'ikey': '',

    # 'reframe_id': [],

    'chem_vendors': [],

    'qid': '',

    'alt_id': '',

    # 'fingerprint': [],

    'similar_compounds': [],

    # 'gvk': [],
    # 'integrity': [],
    # 'informa': [],
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
# gvk_dt = pd.read_csv(os.path.join(data_dir, '2019-06-24_gvk_annotations.csv'))
# integrity_dt = pd.read_csv(os.path.join(data_dir, '2019-04-15_integrity_annotations.csv'))
# informa_dt = pd.read_csv(os.path.join(data_dir, '2019-05-30_informa_annotations.csv'))
annotation_mappings = pd.read_csv(os.path.join(data_dir, 'reframe_annotations_mapping_20200211.csv'))

assay_descr = pd.read_csv(os.path.join(data_dir, 'assay_descriptions_20200427.csv'), header=0)
assay_data = pd.read_csv(os.path.join(data_dir, 'assay_data_20200427.csv'), header=0)
# vendor_dt = pd.read_csv(os.path.join(data_dir, 'portal_info_annot_2020-02-29.csv'), sep=',')
salt_frequencies = pd.read_csv(os.path.join(data_dir, 'salt_frequency_table.csv'))

gvk_dt = pd.read_csv(os.path.join(data_dir, 'gvk_launched_20200414.csv'))
integrity_dt = pd.read_csv(os.path.join(data_dir, 'integrity_launched_20200414.csv'))
informa_dt = pd.read_csv(os.path.join(data_dir, 'informa_launched_20200414.csv'))
adis_dt = pd.read_csv(os.path.join(data_dir, 'adis_launched_20200414.csv'))

vendor_dt = pd.read_csv(os.path.join(data_dir, 'screening_compounds_extended_20200414.csv'))

ikey_wd_map = wdi.wdi_helpers.id_mapper('P235')
compound_id_fp_map = {}
no_charge_map = {}
covered_rfm_ids = set()

rfm_ikey_map = {x['public_id']: (x['ikey'], x['library'], x['source_id'], x['rfm_match_type']) for x in
                vendor_dt[['public_id', 'ikey', 'library', 'source_id', 'rfm_match_type']].to_dict(orient='records')}

ikey_main_label_map = {x['ikey']: x['main_label'] for x in
                       vendor_dt[['ikey', 'main_label']].to_dict(orient='records')}

print('Wikidata compound count:', len(ikey_wd_map))
print('Label count:', len(ikey_main_label_map))


# add unifying ikeys and smiles to vendor data dataframes, use vendor specific id as replacement if
# no ikey can be generated
print('Generating unifiers ...')
gvk_dt = generate_unifiers(gvk_dt, 'sub_smiles', 'gvk_id')
integrity_dt = generate_unifiers(integrity_dt, 'smiles', 'id')
informa_dt = generate_unifiers(informa_dt, 'smiles', 'informa_id')
adis_dt = generate_unifiers(adis_dt, 'full_smiles', 'adis_id')

print('Generating ES documents ...')
generate_vendor_index(gvk_dt, 'gvk', gvk_doc_map)
generate_vendor_index(integrity_dt, 'integrity', integrity_doc_map)
generate_vendor_index(informa_dt, 'informa', informa_doc_map)
generate_vendor_index(adis_dt, 'adis', adis_doc_map)

# for counter, uid in enumerate(gvk_dt['uikey'].unique()):
#     ikey = uid
#     if pd.isnull(ikey):
#         continue
#
#     tmp_obj = copy.deepcopy(reframe_doc)
#     tmp_obj['ikey'] = ikey
#     tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)
#
#     if ikey in ikey_wd_map:
#         tmp_obj['qid'] = ikey_wd_map[ikey]
#
#     for c, x in gvk_dt.iterrows():
#         if x['exclude'] == 1:
#             continue
#
#         single_comp_dict = {}
#         for k, v in gvk_doc_map.items():
#             if pd.isnull(x[k]) or v is None:
#                 continue
#             if type(v) == tuple:
#                 single_comp_dict.update({v[0]: x[k].split(v[1])})
#
#             else:
#                 single_comp_dict.update({v: x[k]})
#
#         if 'smiles' in tmp_obj['gvk']:
#             smiles = single_comp_dict['smiles']
#             main_label = single_comp_dict['drug_name'][0] if len(single_comp_dict['drug_name']) > 0 else ikey
#             # tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
#
#             fp = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
#             if len(fp) > 0:
#                 tmp_obj['fingerprint'] = fp
#
#             d_smiles, d_ikey, _ = desalt_compound(smiles)
#             if len(d_smiles) > 1:
#                 single_comp_dict['sub_smiles'] = d_smiles
#                 single_comp_dict['sub_ikey'] = d_ikey
#
#         tmp_obj['gvk'].append(single_comp_dict)
#
#     update_es(tmp_obj)
#
#     # if c > 20:
#     #     break
#
#     if counter % 100 == 0:
#         print(counter)
#
# for c, x in integrity_dt.iterrows():
#     if x['exclude'] == 1:
#         continue
#
#     ikey = x['ikey']
#     if pd.isnull(ikey):
#         if pd.notnull(x['id']):
#             ikey = str(x['id'])
#         else:
#             continue
#
#     tmp_obj = copy.deepcopy(reframe_doc)
#     tmp_obj['ikey'] = ikey
#     tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)
#
#     if ikey in ikey_wd_map:
#         tmp_obj['qid'] = ikey_wd_map[ikey]
#
#     for k, v in integrity_doc_map.items():
#         if pd.isnull(x[k]) or v is None:
#             continue
#         if type(v) == tuple:
#             tmp_obj['integrity'].update({v[0]: x[k].split(v[1])})
#
#         else:
#             tmp_obj['integrity'].update({v: x[k]})
#
#     if 'smiles' in tmp_obj['integrity']:
#         smiles = tmp_obj['integrity']['smiles']
#         main_label = tmp_obj['integrity']['drug_name'][0] if len(tmp_obj['integrity']['drug_name']) > 0 else ikey
#
#         fp = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
#         if len(fp) > 0:
#             tmp_obj['fingerprint'] = fp
#         d_smiles, d_ikey, _ = desalt_compound(smiles)
#         if len(d_smiles) > 1:
#             tmp_obj['sub_smiles'] = d_smiles
#             tmp_obj['sub_ikey'] = d_ikey
#
#     update_es(tmp_obj)
#
#     if c % 100 == 0:
#         print(c)
#
#
# for c, x in informa_dt.iterrows():
#     if x['exclude'] == 1:
#         continue
#
#     ikey = x['ikey']
#     if pd.isnull(ikey):
#         if pd.notnull(x['informa_id']):
#             ikey = str(x['informa_id'])
#         else:
#             continue
#
#     tmp_obj = copy.deepcopy(reframe_doc)
#     tmp_obj['ikey'] = ikey
#     tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)
#
#     if ikey in ikey_wd_map:
#         tmp_obj['qid'] = ikey_wd_map[ikey]
#
#     for k, v in informa_doc_map.items():
#         if pd.isnull(x[k]) or v is None:
#             continue
#         if type(v) == tuple:
#             tmp_obj['informa'].update({v[0]: x[k].split(v[1])})
#
#         else:
#             tmp_obj['informa'].update({v: x[k]})
#
#     if 'smiles' in tmp_obj['informa']:
#         smiles = tmp_obj['informa']['smiles']
#         main_label = tmp_obj['informa']['drug_name'][0] if len(tmp_obj['informa']['drug_name']) > 0 else ikey
#         fp = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
#         if len(fp) > 0:
#             tmp_obj['fingerprint'] = fp
#         d_smiles, d_ikey, _ = desalt_compound(smiles)
#         if len(d_smiles) > 1:
#             tmp_obj['sub_smiles'] = d_smiles
#             tmp_obj['sub_ikey'] = d_ikey
#
#     update_es(tmp_obj)
#
#     if c % 100 == 0:
#         print(c)

#
# for c, x in vendor_dt.iterrows():
#     ikey = x['ikey']
#     if pd.isnull(ikey):
#         continue
#
#     if not es.exists(index='reframe', doc_type='compound', id=ikey) and ikey in ikey_wd_map:
#         qid = ikey_wd_map[ikey]
#         smiles = x['smiles']
#
#         tmp_obj = copy.deepcopy(reframe_doc)
#         tmp_obj['ikey'] = ikey
#         tmp_obj['reframe_id'], tmp_obj['chem_vendors'] = get_rfm_ids(ikey)
#         tmp_obj['qid'] = qid
#
#         update_es(tmp_obj)
#
#         if pd.notnull(smiles):
#             main_label = tmp_obj['gvk']['drug_name'][0] if len(tmp_obj['gvk']['drug_name']) > 0 else ikey
#             tmp_obj['fingerprint'] = generate_fingerprint(smiles, ikey, main_label, tmp_obj['qid'])
#             d_smiles, d_ikey = desalt_compound(smiles)
#             if len(d_smiles) > 1:
#                 tmp_obj['sub_smiles'] = d_smiles
#                 tmp_obj['sub_ikey'] = d_ikey
#
#     if c % 100 == 0:
#         print(c)


for i in assay_data['ikey'].unique():
    tmp_obj = copy.deepcopy(reframe_doc)
    tmp_obj['ikey'] = i
    ikey = i
    print(i)

    if ikey in ikey_wd_map:
        tmp_obj['qid'] = ikey_wd_map[ikey]

    if ikey in ikey_main_label_map:
        tmp_obj['main_label'] = ikey_main_label_map[ikey] \
            if pd.notnull(ikey_main_label_map[ikey]) else ikey
    else:
        tmp_obj['main_label'] = ikey

    rf, cv, mt = get_rfm_ids(ikey)
    if len(rf) > 0:
        tmp_obj['reframe_id'] = mt
    if len(cv) > 0:
        tmp_obj['chem_vendors'] = cv

    if pd.isnull(ikey):
        continue

    rfm_ids = []
    for c, x in assay_data.loc[assay_data['ikey'] == i, :].iterrows():
        rfm_ids.append(x['rfm_id'])

        # important to use smiles with fixed kekule structure
        if pd.notnull(x['fixed_smiles']):
            tmp_obj['smiles'] = x['fixed_smiles']

        tt = {
            'assay_id': '',
            'title_short': '',
            'indication': ''
        }

        for k, v in assay_data_doc_map.items():
            if pd.isnull(x[k]) or v is None:
                continue

            if k == 'datamode':
                datamode = x['datamode'].upper()

                if datamode.startswith('DECREASING'):
                    tt.update({'activity_type': 'IC50'})
                elif datamode.startswith('INCREASING'):
                    tt.update({'activity_type': 'EC50'})
                elif datamode.startswith('SUPER_ACTIVE'):
                    tt.update({'activity_type': 'SUPER ACTIVE'})

                continue

            if k == 'ac_precision':
                precision = x['ac_precision']
                if precision.lower() == 'equal':
                    tt.update({'ac_precision': ''})
                elif precision.lower() == 'greater than':
                    tt.update({'ac_precision': '>'})
                elif precision.lower() == 'less than':
                    tt.update({'ac_precision': '<'})

                continue

            tt.update({v: x[k]})

            # add indication and short assay title from assay descriptions
            if v == 'assay_id':
                aid = tt['assay_id']
                for cc, ad in assay_descr.iterrows():
                    if aid == ad['assay_id']:
                        tt['assay_title'] = ad['assay_title']
                        tt['title_short'] = ad['title_short']
                        tt['indication'] = ad['indication']

        tmp_obj['assay'].append(tt)

    # make sure to only add an assay to an existing document, or create a new one if document does not exists
    add_assay = False
    if es.exists(index='reframe', doc_type='compound', id=ikey):
        add_assay = True
    elif not es.exists(index='reframe', doc_type='compound', id=ikey) and not any([x in covered_rfm_ids for x in rfm_ids]):
        add_assay = True

    # when adding the assay, make sure, also the fingerprint is being added.
    # This is required here, fingerprint must not end up in similarity index if assay data dont get added to ES.
    if add_assay:
        # when there is no vendor annotation data, make sure there's still a fingerprint
        if not ('fingerprint' in tmp_obj and len(tmp_obj['fingerprint']) > 0) and 'smiles' in tmp_obj and tmp_obj['smiles']:
            fp = generate_fingerprint(tmp_obj['smiles'], ikey, tmp_obj['main_label'], tmp_obj['qid'])
            if len(fp) > 0:
                tmp_obj['fingerprint'] = fp

        update_es(tmp_obj)

    covered_rfm_ids.update(rfm_ids)

# print('adding stereofree matches ...')
# stereofree_list = [x[:15] for x in compound_id_fp_map.keys() if pd.notnull(x) and len(x) > 15]
# for i in vendor_dt['ikey'].unique():
#     if es.exists(index='reframe', doc_type='compound', id=i):
#         continue
#
#     if pd.isnull(i) or (pd.notnull(i) and i[:15] not in stereofree_list):
#         continue
#
#     tmp_obj = copy.deepcopy(reframe_doc)
#     tmp_obj['ikey'] = i
#     ikey = i
#     print(i)
#
#     if ikey in ikey_wd_map:
#         tmp_obj['qid'] = ikey_wd_map[ikey]
#
#     rf, cv = get_rfm_ids(ikey)
#     if len(rf) > 0:
#         tmp_obj['reframe_id'] = rf
#     if len(cv) > 0:
#         tmp_obj['chem_vendors'] = cv
#
#     if pd.isnull(ikey):
#         continue
#
#     for c, x in vendor_dt.loc[vendor_dt['ikey'] == i, :].iterrows():
#
#         if pd.notnull(x['fixed_smiles']):
#             tmp_obj['smiles'] = x['fixed_smiles']
#
#             # when there is no vendor annotation data, make sure there's still a fingerprint
#             if not ('fingerprint' in tmp_obj and len(tmp_obj['fingerprint']) > 0):
#                 fp = generate_fingerprint(x['smiles'], ikey, x['fixed_smiles'], tmp_obj['qid'])
#                 if len(fp) > 0:
#                     tmp_obj['fingerprint'] = fp
#
#     update_es(tmp_obj)


for c, (compound_id, values) in enumerate(compound_id_fp_map.items()):
    _, main_label, qid, fp = values

    found_cmpnds = []
    for r_id, (_, r_label, r_qid, r_fp) in compound_id_fp_map.items():
        if compound_id == r_id:
            continue

        tnmt = calculate_tanimoto(fp, r_fp)
        if tnmt > 0.82:
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
         # 'ONPGOSVDVDPBCY-CQSZACIVSA-N',
         'WXJFKKQWPMNTIM-VWLOTQADSA-N'
         ]

example_data = {}

for c, x in enumerate(qids):
    r = es.get(index="reframe", doc_type='compound', id=ikeys[c])['_source']
    example_data.update({x: r})

with open('example_data.json', 'w') as outfile:
    json.dump(example_data, outfile)

