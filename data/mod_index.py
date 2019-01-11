import json
import os
import argparse

from elasticsearch import Elasticsearch
es = Elasticsearch()

# command line arguments
parser = argparse.ArgumentParser(description='ES Index Change')
parser.add_argument('--id', '-d',  metavar='X', type=str,
                        help='ID of index to modify')
parser.add_argument('--index', '-i', metavar='Y', help='ES index')
parser.add_argument('--data', '-a', metavar='<data>', help='Data to modify', type=str)
args = parser.parse_args()

index = args.index
index_id = args.id
data = args.data

print(index, index_id, data)
result = es.get(index=index, doc_type='compound', id=index_id)

dt = result['_source']

del_path = '/informa'
splits = del_path.split('/')
for c, x in enumerate(splits):
    if x:
        del dt[x]

es.update(index=index, id=index_id, doc_type='compound', body={'doc': dt})

print(result)
print(json.loads(data.strip("'")))


