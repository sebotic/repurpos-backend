import json
import pandas as pd
import os

from elasticsearch import Elasticsearch
es = Elasticsearch()

data_dir = os.getenv('DATA_DIR')
vendor_dt = pd.read_csv(os.path.join(data_dir, 'portal_info_annot.csv'), sep=',')

rfm_ikey_map = {x['public_id']: (x['ikey'], x['library'], x['source_id']) for x in
                vendor_dt[['public_id', 'ikey', 'library', 'source_id']].to_dict(orient='records')}


def get_reframe(ikey):
    rfm_dt = [(x, v[0], v[1], v[2]) for x, v in
              rfm_ikey_map.items() if v[0] == ikey]
    return rfm_dt


doc_list = []
reframe_smiles_map = {
    'compound_id': [],
    'smiles': []

}

full_smiles_map = {
    'compound_id': [],
    'normalized_smiles': [],
    'vendor': [],
    'vendor_id': [],
}


def process_batch(batch):
    for count, hit in enumerate(batch['hits']['hits']):
        compound_id = hit['_id']
        full_doc = es.get(index='reframe', doc_type='compound', id=compound_id)
        doc_list.append(full_doc)

        print(compound_id)

        if 'smiles' in full_doc['_source']:
            full_smiles = full_doc['_source']['smiles']
        else:
            full_smiles = ''

        for x in ['gvk', 'integrity', 'informa']:
            if x in full_doc['_source'] and len(full_doc['_source'][x] ) > 0:
                for z in full_doc['_source'][x]:
                    if x + '_id' in z:
                        data_vendor_id = z[x + '_id']
                    else:
                        data_vendor_id = z['id']

                    full_smiles_map['compound_id'].append(compound_id)
                    full_smiles_map['normalized_smiles'].append(full_smiles)
                    full_smiles_map['vendor'].append(x)
                    full_smiles_map['vendor_id'].append(data_vendor_id)

        for rf in get_reframe(compound_id):
            # add reframe id first
            full_smiles_map['compound_id'].append(compound_id)
            full_smiles_map['normalized_smiles'].append(full_smiles)
            full_smiles_map['vendor'].append('reframe')
            full_smiles_map['vendor_id'].append(rf[0])

            # add chem vendor after
            full_smiles_map['compound_id'].append(compound_id)
            full_smiles_map['normalized_smiles'].append(full_smiles)
            full_smiles_map['vendor'].append(rf[2])
            full_smiles_map['vendor_id'].append(rf[3])

        if 'reframe_id' in full_doc['_source'] and (full_doc['_source']['reframe_id'][0] is True or
                                                    full_doc['_source']['reframe_id'][0] == 'skeleton'):

            if 'smiles' in full_doc['_source']:
                reframe_smiles_map['compound_id'].append(compound_id)
                reframe_smiles_map['smiles'].append(full_doc['_source']['smiles'])


body = {
    "_source": {
        "includes": ['ikey'],
    },
    "query": {
        "query_string": {

            "query": "*",
            # "fields": ['fingerprint', 'smiles']
        }
    },
    "sort": [
        "_doc"
    ]
}

es.indices.refresh(index="reframe")

r = es.search(index="reframe", body=body, scroll='1m')
scroll_id = r['_scroll_id']
process_batch(r)

counter = 0
while True:
    r = es.scroll(scroll_id=scroll_id, scroll='1m')
    counter += 1
    #     print('batch processed:', counter)
    if len(r['hits']['hits']) == 0:
        break

    process_batch(r)

print('Total count of compound fingerprints:', len(doc_list))
print('Total Reframe compounds', len(reframe_smiles_map['compound_id']))

with open('es_dump.json', 'w') as outfile:
    json.dump(doc_list, outfile)

df = pd.DataFrame.from_dict(reframe_smiles_map)
df.to_csv('reframe_smiles.csv')

df_all = pd.DataFrame.from_dict(full_smiles_map)
df_all.to_csv('reframedb_full_map.csv')
